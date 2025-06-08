#!/usr/bin/env python3

from scraper import WigleQuery
import os
import logging
from sqlwrap import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wigle_query():
    test_ssid = 'linksys'
    logger.info(f"Testing Wigle API with SSID: {test_ssid}")
    token = os.getenv('WIGLE_API_TOKEN')
    if token:
        logger.info(f"Using auth token: {token[:10]}...")
    else:
        logger.warning("No Wigle API token found in environment!")
    scraper = WigleQuery(auth_token=token)
    response = scraper.query(test_ssid)
    logger.info("Raw API Response:")
    logger.info(f"Found {len(response)} results")
    logger.info("Storing results in database...")
    list(scraper.store_results(test_ssid, response, db_path='probemap.db'))
    # Verify database contents
    with Database('probemap.db') as db:
        stored_coords = list(db.get_ssid_coords(test_ssid))
        logger.info(f"Retrieved {len(stored_coords)} locations from database:")
        for coord in stored_coords:
            logger.info(f"  {coord}")
        # Extra debug: count rows directly
        db.cursor.execute("SELECT COUNT(*) FROM ssid_to_coords WHERE ssid = ?", (test_ssid,))
        count = db.cursor.fetchone()[0]
        logger.info(f"Direct row count for SSID '{test_ssid}': {count}")
    # Clean up: delete the test SSID from the database
    with Database('probemap.db') as db:
        db.cursor.execute("DELETE FROM ssid_to_coords WHERE ssid = ?", (test_ssid,))
        db.conn.commit()
        logger.info(f"Cleaned up: deleted test SSID '{test_ssid}' from database.")

if __name__ == "__main__":
    test_wigle_query() 