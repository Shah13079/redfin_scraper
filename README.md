# redfin_scraper
### Goal <br />
Collect the amount of search results for a list of search terms on RedFin with 2 filters turned on (property type = land, include=sold-3mo & ,include=sold-1mo or none).

### Input <br />
A CSV with two columns. First column is County. Second Column is State. Combine these two in the following format for the search input into RedFin: "{COUNTY}, {STATE}"
Example: Hampshire County, NC.

### Output <br />
A new CSV with the listing, count for For Sale, Sold in 1 Month, and Sold in 3 Month.

### Behavior of Script <br />
1. Read CSV file
2. For each row in CSV file, determine correct search URL with the following search parameters: {COUNTY}, {STATE}
3. Collect search result count for "For Sale" listings with Home Type filter of "Land"
4. Add value to Available column in new CSV for row
5. Collect search result count for "Sold --> Last 1 Month" listings with Home Type filter of Land
6. Collect search result count for "Sold --> Last 3 Months" listings with Home Type filter of Land
7. Repeat for next row
8. Save CSV with the following format: redfin_counties_velocity_%Y-%m-%d %H-%M-%S.


### Technologies <br />
Python Scrapy framework is entirely used in this project. 

### Technical approach <br />
1. The program first take location from list of csv.
2. Find out its latitude and longitude coordinates by calling a third party API.
3. Sending request to another URL combination of Google map and redfin website, to get route search URL for location.
4. Then sending request to route URL with different filters and saving data into csv file.

### Run the Program <br />
1. Install required dependecies by ( pip install -r requirements.txt) in cmd (at project directory).
2. command: scrapy crawl final



