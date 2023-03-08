import json
import scrapy
import requests
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim
from urllib.parse import urlencode
from w3lib.html import remove_tags


class FileSpider(scrapy.Spider):
    name = "final"
    allowed_domains = ["www.redfin.com"]

    date_is = datetime.strftime(datetime.today(), "%Y-%m-%d %H-%M-%S")

    custom_settings = {
        "FEEDS": {f"redfin_counties_velocity_{date_is}.csv": {"format": "csv"}}
    }

    request_headers = {
        "authority": "www.redfin.com",
        "method": "GET",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
              (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    def start_requests(self):
        """This function is called when the spider is started."""
        df = pd.read_csv(r"RedFinCounties.csv")
        for index, row in df.iterrows():
            county = row["County"]
            state = row["State"]
            if "County" not in county:
                county = county + " County"

            # Calling static utility function for getting search url according to location
            route_url = FileSpider._find_address_bounds(
                {"state": state, "county": county}
            )
            if route_url is None:
                continue

            yield scrapy.Request(
                url=f"https://www.redfin.com{route_url}/filter/property-type=land",
                callback=self.for_sale_availble,
                headers=self.request_headers,
                meta={"route_url": route_url, "state": state, "county": county},
            )

    def for_sale_availble(self, response):
        """This method get properties count available for sale.

        Args:
            response (selector object): response from the request.

        Yields:
            Request: sending request to next URL with other filters & parameters.
        """
        route_url = response.meta["route_url"]
        state = response.meta["state"]
        county = response.meta["county"]

        for_sale = response.xpath("//div[@class='homes summary']").get()
        for_sale = FileSpider._clean_html(for_sale)

        yield scrapy.Request(
            url=f"https://www.redfin.com{route_url}/filter/property-type=land,include=sold-1mo",
            callback=self.sold_in_month,
            headers=self.request_headers,
            meta={
                "for_sale": for_sale,
                "route_url": route_url,
                "state": state,
                "county": county,
            },
        )

    def sold_in_month(self, response):
        """This method get properties count sold in recent one month."""
        route_url = response.meta["route_url"]
        state = response.meta["state"]
        county = response.meta["county"]
        for_sale = response.meta["for_sale"]

        sold_in_month = response.xpath("//div[@class='homes summary']").get()
        sold_in_month = FileSpider._clean_html(sold_in_month)

        yield scrapy.Request(
            url=f"https://www.redfin.com{route_url}/filter/property-type=land,include=sold-3mo",
            callback=self.sold_in_three_months,
            headers=self.request_headers,
            meta={
                "for_sale": for_sale,
                "sold_in_month": sold_in_month,
                "state": state,
                "county": county,
            },
        )

    def sold_in_three_months(self, response):
        """This method get properties count sold in recent three months."""
        state = response.meta["state"]
        county = response.meta["county"]
        for_sale = response.meta["for_sale"] or 0
        sold_in_month = response.meta["sold_in_month"] or 0
        sold_in_three_month = response.xpath(
            "//div[@class='homes summary']").get()

        sold_in_three_month = FileSpider._clean_html(sold_in_three_month)

        final_data = {
            "county": county,
            "state": state,
            "for_sale": for_sale,
            "sold_in_month": sold_in_month,
            "sold_in_three_month": sold_in_three_month,
        }

        yield final_data
        print(final_data)

    @staticmethod
    def _find_address_bounds(addresses):
        """Generate latitude and longitude bounds for a given address.

        Args:
            addresses (dictionary): containing address e.g county, state, etc

        Returns:
            str: resulting url string got from next function call
        """
        # unpacking arguments from dictionary
        county = addresses["county"]
        state = addresses["state"]

        # Initialize Nominatim API
        geolocator = Nominatim(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                  (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        location = geolocator.geocode(f"{county}, {state}")

        location_details = {
            "latitude": location.latitude,
            "longtitude": location.longitude,
            "county": county,
            "state": state,
        }

        return FileSpider._get_google_map_address(location_details)

    @staticmethod
    def _get_google_map_address(location_details):
        """pushing payload to redfin-google-map API to get route search URL for location.

        Args:
            location_details (dictionary): taking dictionary consist of address and coordinates

        Returns:
            str: return URL that match with location(county, city) and state
        """

        lat = location_details["latitude"]
        lng = location_details["longtitude"]
        county = location_details["county"].strip()
        state = location_details["state"]

        params = {
            "location": "%s %s" % (county, state),
            "start": "0",
            "count": "10",
            "v": "2",
            "market": "false",
            "iss": "false",
            "ooa": "true",
            "mrs": "false",
            "region_id": "NaN",
            "region_type": "NaN",
            "lat": "%s" % lat,
            "lng": "%s" % lng,
        }

        final_url = (
            "https://www.redfin.com/stingray/do/location-autocomplete?"
            + urlencode(params)
        )

        response = requests.get(
            url=final_url, headers=FileSpider.request_headers)

        json_response = json.loads(response.text.replace("{}&&", ""))

        rows = json_response["payload"].get("sections")[0].get("rows")

        for each in rows:
            name = each.get("name")
            url = each.get("url")

            if (
                f"/{state}"
                and "/%s" % (county.replace(" ", "-")) in url
                and name == county
            ):
                return url

    @staticmethod
    def _clean_html(html):
        """Remove html tags from a string and return required values."""
        text = remove_tags(html)
        if "of" in text:
            clean_text = text.split("of")[-1]
            return "".join(filter(str.isdigit, clean_text))
        return "".join(filter(str.isdigit, text))
