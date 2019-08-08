"""
Pipeline
========

	The pipeline internal package is the one responsible for doing the
scraping. It is composed of a producer, a series of stages and a consumer.

	For Scrapedia the producer takes the form of a requester, responsible for
fetching Futpédia's web pages and dispatching its contents to subsequent
stages.

	The first stage following the producer is the seeker, being specialized
for each web page. It searches for specific excerpts on the web pages'
contents to send to the next stage.

	The second stage is the parser, being specialized for each web page like
the seeker. It receives a string and parses it, sending only the data of
interest to the final stage of the pipeline.

	The consumer and final stage of the pipeline is the packer. The packer
receives the data of interest and uses it to build a suitable data schema for
the response.
"""

from .pipeline import Pipeline


__all__ = ['errors', 'pipeline']
