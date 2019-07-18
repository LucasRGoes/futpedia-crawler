# Changelog

## v0.1.0

* 06-16-2019:
	* Started structuring project;
	* Started implementing scraper module with its first class: Scrapedia;
	* Created errors module for Scrapedia's custom errors;
	* Started creating unit tests for the class Scrapedia;
	* Added cache tools to Scrapedia;
	* Segmented requesting methods (\_\_full_teams, \_\_full_championships) from accessible methods (teams, championships) to use the cache internally at Scrapedia instances;
	* Added ScrapediaChampionship class to access data related to specific championships;

* 06-17-2019:
	* Added session usage to requests object to enable retrying of requests based on the status code;
	* Started creation of the fetch method of championships;
	* Created utils package;
