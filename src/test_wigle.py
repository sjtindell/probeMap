#!/usr/bin/env python3

from scraper import WigleQuery
import os
import logging
from sqlwrap import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wigle_query():
    # Test with a specific SSID
    test_ssid = "linksys"
    query = WigleQuery(test_ssid)
    
    logger.info(f"Testing Wigle API with SSID: {test_ssid}")
    logger.info(f"Using auth token: {os.getenv('WIGLE_API_TOKEN')[:10]}...")
    
    # First test the raw response
    response = query.response
    if response:
        logger.info("Raw API Response:")
        logger.info(f"Found {len(response.get('results', []))} results")
    
    # Store results in database
    logger.info("Storing results in database...")
    coords = list(query.store_results())
    logger.info(f"Stored {len(coords)} locations")
    
    # Verify database contents
    with Database('../ssids.db') as db:
        stored_coords = list(db.get_ssid_coords(test_ssid))
        logger.info(f"Retrieved {len(stored_coords)} locations from database:")
        for lat, lon, country, region, city in stored_coords:
            location = f"{city}, {region}" if city and region else region or country or "Unknown"
            logger.info(f"  Lat: {lat}, Lon: {lon} ({location})")

if __name__ == "__main__":
    test_wigle_query() 