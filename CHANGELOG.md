Changelog
=========

## v0.1.0

* __06-16-2019__:
	* Started structuring project;
	* Started implementing scraper module with its first class: Scrapedia;
	* Created errors module for Scrapedia's custom errors;
	* Started creating unit tests for the class Scrapedia;
	* Added cache tools to Scrapedia;
	* Segmented requesting methods (\_\_full_teams, \_\_full_championships) from accessible methods (teams, championships) to use the cache internally at Scrapedia instances;
	* Added ScrapediaChampionship class to access data related to specific championships;

* __06-17-2019__:
	* Added session usage to requests object to enable retrying of requests based on the status code;
	* Started creation of the fetch method of championships;
	* Created utils package;

* __06-18-2019__:
	* Updated README files and documentation;
	* Created Jupyter notebooks to document the usage of the module;
	* Using a VERSION file for version control of the project;
	* Added a ScraperCore class to hold common functions of all of the project's scrapers;
	* Rewriting scraper classes and renaming them in order to facilitate understanding;
	* Renamed custom exceptions and added a core one so that others can extend from it;
	* Created error for data from Futpédia that is not found on the requested or cached data;
