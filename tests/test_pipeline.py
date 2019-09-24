"""Collection of unit tests for scrapedia.pipeline module's classes and functions.

Classes: PipelineTests, PipelineFactoryTests
"""

import unittest

from scrapedia.pipeline import Pipeline, PipelineFactory


def mock_function(number):
	return number + 1


class PipelineTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a Pipeline, its methods
	and static methods of its class.

	Tests: test_scrap, test_create_producer, test_create_stage,
	test_create_consumer
	"""
	def test_scrap(self):
		"""Steps:
		1 - Instantiates a Pipeline
		2 - Use scrap() and verify the result
		3 - Verify if it raises error with only two functions when building the
		instance
		4 - Verify if it raises error with one of the arguments not being a
		function
		"""
		pipe = Pipeline(mock_function, mock_function, mock_function)
		self.assertEqual(pipe.scrap(1), 4)

		with self.assertRaises(ValueError):
			pipe = Pipeline(mock_function, mock_function)

		with self.assertRaises(ValueError):
			pipe = Pipeline(mock_function, mock_function, False)

	def test_create_producer(self):
		"""Steps:
		1 - Creates a consumer, two stages and a producer with mock functions
		2 - Send the producer a parameter and verify the return value
		"""
		consumer = Pipeline.create_consumer(mock_function)
		next(consumer)

		stage1 = Pipeline.create_stage(mock_function, consumer)
		next(stage1)

		stage2 = Pipeline.create_stage(mock_function, stage1)
		next(stage2)

		producer = Pipeline.create_producer(mock_function, stage2)
		next(producer)

		try:
			producer.send(1)
		except StopIteration as res:
			self.assertEqual(res.value, 5)

	def test_create_stage(self):
		"""Steps:
		1 - Creates a consumer and two stages with mock functions
		2 - Send the first stage a parameter and verify the return value
		"""
		consumer = Pipeline.create_consumer(mock_function)
		next(consumer)

		stage1 = Pipeline.create_stage(mock_function, consumer)
		next(stage1)

		stage2 = Pipeline.create_stage(mock_function, stage1)
		next(stage2)

		try:
			stage2.send(1)
		except StopIteration as res:
			self.assertEqual(res.value, 4)

	def test_create_consumer(self):
		"""Steps:
		1 - Creates a consumer with a mock function
		2 - Send it a parameter and verify the return value
		"""
		consumer = Pipeline.create_consumer(mock_function)
		next(consumer)

		try:
			consumer.send(1)
		except StopIteration as res:
			self.assertEqual(res.value, 2)


class PipelineFactoryTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a PipelineFactory and its
	methods.

	Tests: test_build
	"""
	def test_build(self):
		"""Steps:
		1 - Instantiates a PipelineFactory
		2 - Use build('championships') and verify the resulting Pipeline
		3 - Use build('unknown') and verify if it raises an error
		"""
		factory = PipelineFactory()
		pipeline = factory.build('championships')
		self.assertIsInstance(pipeline, Pipeline)

		with self.assertRaises(ValueError):
			factory.build('unknown')


if __name__ == 'main':
	unittest.main()
