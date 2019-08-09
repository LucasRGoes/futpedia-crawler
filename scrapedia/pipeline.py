"""The pipeline module is the one responsible for doing the scraping. It is
composed of a producer, a series of stages and a consumer.

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

Classes: Pipeline
"""

class Pipeline(object):
	"""The Pipeline class follows a Pipeline design pattern proposed by
	Lorenzo Bolla (https://lbolla.info/pipelines-in-python). It is composed of
	a producer, a series of stages and a consumer that are used together to
	scrap a web page.

	Methods: start

	Static Methods: create_producer, create_stage, create_consumer
	"""
	def __init__(self, *args):
		"""Pipeline's constructor. It iterates over the arguments to build the
		pipeline using the chosen functions.

		Parameters
		----------
		*args -- a list of functions used to build the pipeline
		"""
		if len(args) < 3:
			raise ValueError(
				'the minimum number of arguments to build a pipeline is 3')

		if not all(type(x).__name__ == 'function' for x in args):
			raise ValueError('all arguments should be functions')

		consumer = Pipeline.create_consumer(args[-1])
		next(consumer)

		temp = consumer
		for func in reversed(args[1:-1]):
			stage = Pipeline.create_stage(func, temp)
			next(stage)
			temp = stage

		producer = Pipeline.create_producer(args[0], temp)
		next(producer)

		self._pipeline = producer

	def scrap(self, url: str):
		"""Starts the pipeline, executes each stage and returns the results of
		the scraping over the web page served by the chosen URL.

		Returns -- the information of interest scraped from the web page
		"""
		try:
			self._pipeline.send(url)
		except StopIteration as res:
			self._pipeline.close()
			return res.value

	@staticmethod
	def create_producer(func, next_stage):
		"""Creates a producer, the first stage of a pipeline.
	
		Parameters
		----------
		func -- the function to be executed by the stage
		next_stage -- the stage to be called after the current one ends the
		execution of its function

		Returns -- result of the next stage
		"""
		tmp = (yield)
		try:
			next_stage.send(func(tmp))
		except StopIteration as res:
			next_stage.close()
			return res.value

	@staticmethod
	def create_stage(func, next_stage):
		"""Creates a middle stage of a pipeline.
	
		Parameters
		----------
		func -- the function to be executed by the stage
		next_stage -- the stage to be called after the current one ends the
		execution of its function

		Returns -- result of the next stage
		"""
		tmp = (yield)
		try:
			next_stage.send(func(tmp))
		except StopIteration as res:
			next_stage.close()
			return res.value

	@staticmethod
	def create_consumer(func):
		"""Creates a consumer, the final stage of a pipeline.
	
		Parameters
		----------
		func -- the function to be executed by the consumer

		Returns -- result of the function
		"""
		tmp = (yield)
		return func(tmp)
