Changelog
=========

## v0.1.0

* __07-16-2019__:
	* Started structuring project;
	* Started implementing scraper module with its first class: Scrapedia;
	* Created errors module for Scrapedia's custom errors;
	* Started creating unit tests for the class Scrapedia;
	* Added cache tools to Scrapedia;
	* Segmented requesting methods (\_\_full_teams, \_\_full_championships) from accessible methods (teams, championships) to use the cache internally at Scrapedia instances;
	* Added ScrapediaChampionship class to access data related to specific championships;

* __07-17-2019__:
	* Added session usage to requests object to enable retrying of requests based on the status code;
	* Started creation of the fetch method of championships;
	* Created utils package;

* __07-18-2019__:
	* Updated README files and documentation;
	* Created Jupyter notebooks to document the usage of the mdoule;
	* Used a VERSION file for version control of the project;
	* Added a ScraperCore class to hold common functions of all of the project's scrapers;
	* Rewrited scraper classes and renamed them in order to facilitate understanding;
	* Renamed custom exceptions and added a core one so that others can extend from it;
	* Created error for data from Futpédia that is not found on the requested or cached data;
	* Updated tests to reflect changes to code;

* __07-22-2019__:
	* Modified identification logic at cached objects;
	* Updated ChampionshipScraper.fetch() to seasons();
	* Started creation of unit tests for ChampionshipScraper;

* __07-26-2019__:
	* Removed utils.py module. A better practice is trying to solve everything in a 'pythonic' way;
	* Removed logger usage at scrapers. A better practice is to raise errors concerning the problem that occured;
	* Renamed errors;
	* Changed lists to pandas.DataFrame on most of the scrapers functions;
	* Updated tests to cover new return types;

* __07-30-2019__:
	* Corrected bug at ChampionshipScraper.\_\_scrap_seasons() where the '/' char was being used at the URL before the endpoint;
	* Created a scraper to fetch data concerning specific seasons of a championship;
	* Changed ChampionshipScraper.seasons() so that the 'target' parameter is now optional, the default is to fetch all seasons;
	* Changed default number of retries on a request;

* __07-31-2019__:
	* Created test for ChampionshipScraper.seasons();
	* Solved bug at ChampionshipScraper.\_\_scrap_seasons() where the content for Brasileiro Unificado could not be transformed as the other pages;

* __08-03-2019__:
	* Created test for ChampionshipScraper.season();
	* Created test for SeasonScraper.status();
	* Updated season() and championship() to use their parents class request_retries parameter when building new scrapers;
	* Removed Brasileiro Unificado from championships() options as it would be more difficult to adequate the crawler to it and there are alternatives like getting each of its three championships separately;
	* Added global parameter to test_scrapers to set the request_retries parameter of the scrapers;

* __08-07-2019__:
	* Started creation of parsing paths for a season's games based on that year's format;
	* Modified README.md and documentation files to indicate that the project is only a web scraper and not a web crawler; 
	* Created outline of new project structure;
	* Created seekers.py to hold only code concerning searching of raw data at requested pages;
	* Using pipeline design pattern for new structure;
	* Created new error class considering new structure;
	* Created models to hold Futpédia's parsed data;
	* Created parsers.py to hold only code concerning the parsing of raw data obtained from Futpédia's pages;
	* Added project's architecture;
	* Created pipeline internal package to hold any code related to scraping aspects of the project;
	* Created errors.py for the pipeline internal package;
	* Created Pipeline class and tests for its methods;

* __08-08-2019__:
	* Started reorganizing modules;
	* Added errors for each possible stage of a scraping pipeline;
	* Created Requester class and tests for its methods;
	* Completed Requester tests;
	* Redocumented seekers module and created tests for it;
	* Completed seekers module tests;
	* Updated status list of requester module;
	* Created SeasonParser and TeamParser at parsers module;
	* Created tests for parsers module;
	* Created packers module, its classes and its tests;
	* Removed ScrapediaPackError as there was no need for it;
	* Changed retry_limit at test_requester;
