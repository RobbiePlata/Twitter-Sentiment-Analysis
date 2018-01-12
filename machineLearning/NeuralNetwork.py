import tensorflow as tf
import numpy as np

class NeuralNetowork:

    def __init__(self):
        self.output = None      # List of classifications: good, neutral, or bad
        self.input = None       # List of Tweet objects that were fed into the network
        self.error = 0          # Incorrectness of the networks guesses, i.e. error = ||Outputs - TrueLables||^2
        self.numberOfClasses = 3  # Number of potential outputs, i.e. |{good=1, neutral=0, bad=-1}|


    def convertTweets(self):
        """
        converts tweets into usable tensors
        :return: None
        """
        #TODO Andrew: create a function that parces tweets to tensors

    def constructNetwork(self, tweetLength):
        """
        Create the neuralnetwork and its layers
        :param tweetLength: length of a tweet
        :return: None
        """
        #TODO Andrew: create a function that builds the computational graph

        # Sizes that will be used for the convolutional and fully connected layers.
        numberOfConvolutionalLayers = 5
        filterSizes = {2, 3, 4, 5, 6}
        numberOfFilters = {10, 10, 10, 10, 10}
        numberOfFullyConnectedLayers = 2
        fullyConnectedSize = 180
        # Number of tweets to be analysed at a time, higher number yields faster convergence, but requires more RAM
        tweetsPerBatch = 250

        # Arbitrary number of vectors with length tweetLength
        x = tf.placeholder(tf.float32, [None, tweetLength], name='x')
        # Reshapes x to be 3d so that convolution can be applied
        xTweet = tf.reshape(x, [-1, tweetLength, 1])
        # Tensor storing all the true labels for each tweet in our training batch
        yTrue = tf.placeholder(tf.float32, shape=[None, self.numberOfClasses], name='yTrue')

        # Constructs the computational graph.
        # This graph will be set up such that Layers = {1, 2, 3, ..., n}, where 1 is the first layer, and n is the last
        # The set of directed connections will be Connections = {(a, b): a,b\in Layers && a < b }
        # That is each layer is connected to every layer in front of it
        # We do this for two reasons, the first being that is solves the problem of the vanishing gradient
        #                             the second being that it helps give more equal priority to all convolutions
        convolutionalLayers = [numberOfConvolutionalLayers]
        convolutionalWeights = [numberOfConvolutionalLayers]
        # Starting input, input will be updated such that each layer takes in input from all previous layers
        input = xTweet
        # Similarly the number of input channels will be updated
        numberOfInputChannels = 1

        # Creates the convolutional layers
        for i in range(numberOfConvolutionalLayers):
            convolutionalLayers[i], convolutionalWeights[i] =\
                self.newConvolutionalLayer(input=input, numberOfInputChannels=numberOfInputChannels,
                                           filterSize=filterSizes[i], numberOfFilters=numberOfFilters[i],
                                           use2x2pooling=False)

            # Adds the output from the current layer to the tensor of all the previous layers' outputs
            input = tf.concat(input, convolutionalLayers[i])

            # Updates the number of input channels so that all previous layers' inputs are taken into account
            numberOfInputChannels = 0
            for j in range(i):
                numberOfInputChannels += numberOfFilters[j]


        fullyConnectedLayers = [numberOfFullyConnectedLayers]
        numberOfFeautres = [numberOfFullyConnectedLayers]

        # Reshapes the input tensor to 1D so that it can be run through a fully connected layer
        flattenedInput = self.flattenLayer(input)

        # Creates a fully connected layer
        fullyConnectedLayers[0] = self.newFullyConnectedLayer(input=flattenedInput, numberOfInputs=numberOfFeautres,
                                                              numberOfOutputs=fullyConnectedSize, useRelu=True)

        # Updates the input and number of inputs
        flattenedInput = tf.concat(flattenedInput, fullyConnectedLayers[0])
        numberOfFeautres += fullyConnectedSize

        # Creates the last layer of the network
        fullyConnectedLayers[1] = self.newFullyConnectedLayer(input=flattenedInput, numberOfInputs=numberOfFeautres,
                                                              numberOfOutputs=self.numberOfClasses, useRelu=True)


    def newWeights(self, shape):
        """
        Generates new weights for a layer
        :param shape: dimensions of the weight tensor
        :return: a tensor of weights
        """
        return tf.Variable(tf.truncated_normal(shape, stddev=0.5))

    def newBiases(self, shape):
        """
        Generates new biases for a layer
        :param shape: dimensions of the biases tensor
        :return: a tensors of biases
        """
        return tf.Variable(tf.constant(0.05, shape=[shape]))

    def newConvolutionalLayer(self, input, numberOfInputChannels, filterSize, numberOfFilters, use2x2pooling=True):
        """
        Creates a new convolutional layer
        :param input: previous layer's output
        :param numberOfInputChannels:  number of outputs (number of neurons) in the previous layer
        :param filterSize: size of the filter (kernel)
        :param numberOfFilters: number of such filters
        :param use2x2pooling: downscales the output tensor such that each quadrant of 4 is is squished down to a single unit
        :return: a tensor that is the output of the layer along with the associated weights
        """
        # Shape out the filters' weights
        weightShape = [filterSize, numberOfInputChannels, numberOfFilters]

        # Shape of the filters biases
        biasesShape = [numberOfFilters]

        # Creates containers for weights and biases of the filters
        weights = self.newWeights(shape=weightShape)
        biases = self.newBiases(shape=biasesShape)

        # Initializes a 2d convolutional layer
        # strides = [1, y-axis movement units, x-axis movement units, 1]
        # padding = 'SAME' => tensor is given extra dimensions of zeros if needed
        layer = tf.nn.conv1d(value=input, filters=weights, stride=1, padding='SAME')

        # Adds biases to layer
        layer += biases

        if use2x2pooling:
            # Adds a pooling filter to the layer
            # pooling takes each 2x2 region, say R, and projects it to a 1x1 region, say B, via B = max(R)
            layer = tf.nn.max_pool(value=layer, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

        # Adds a ReLU activation function to the layer, ReLU = Rectified Linear Unit
        # ReLU activation changes the original output, say V, to O = max(0, V), i.e. all negative outputs are set to 0
        layer = tf.nn.relu(layer)

        return layer, weights


    def flattenLayer(self, layer):
        """
        The output of convolutional layers is tensors with 3 or dimensions
        The function will scale down the dimension of the output tensor so that it may be feed into the next layer
        :param layer: current layer's output
        :return: flattened output and number of features of the current layer
        """

        # Get dimension of the layer
        layerShape = layer.get_shape()

        numberOfFeatures = np.array(layerShape[1:3], dtype=int).prod()

        # Reshapes the current layer's output
        flatLayer = tf.reshape(layer, [-1, numberOfFeatures])
        return flatLayer, numberOfFeatures

    def newFullyConnectedLayer(self, input, numberOfInputs, numberOfOutputs, useRelu=True):
        """
        Creates a new fully connected layer
        :param input: previous layer of the model
        :param numberOfInputs: number of outputs(neurons) from the previous layer
        :param numberOfOutputs: number of outputs of this layer
        :param useRelu: if true then output = max(0, output)
        :return: a new fully connected layer
        """

        # Initializes new containers for weights and biases
        weights = self.newWeights(shape=[numberOfInputs, numberOfOutputs])
        biases = self.newBiases(shape=[numberOfOutputs])

        # Creates a new layer which is the matrix multiplication of the weights summed with the biases matrix
        layer = tf.matmul(input, weights) + biases

        # Adds ReLU activation, that is output = max(output, 0)
        if useRelu:
            layer = tf.nn.relu(layer)

        return layer

