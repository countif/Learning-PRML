import numpy as np
from NeuralNetwork.NetworkComponent import OutputNetworkLayer


class BPPerceptron:
    """
    Single BPPerceptron, perceptron with only input and ouput layer
    Notes: this is the interface with param check
    """
    def __init__(self, n_input, n_output, n_neurons):
        # TODO: param check
        self._n_input = n_input
        self._n_output = n_output
        self._layer = OutputNetworkLayer(n_priors=n_input, n_neurons=n_neurons)

    def train(self, x, y):
        x = np.array(x)
        y = np.array(y)
        assert x.shape == (self._n_input,)
        assert y.shape == (self._n_output,)
        self._layer.train(x, y)

    def train_many(self, x, y):
        x = np.array(x)
        y = np.array(y)
        assert x.shape[1] == self._n_input
        assert y.shape[1] == self._n_output
        assert x.shape[0] == y.shape[0]
        for xrow, yrow in zip(x, y):
            self._layer.train(xrow, yrow)

    def predict(self, x):
        x = np.array(x)
        assert len(x.shape) == 1 and x.shape[0] == self._n_input
        return self._layer.predict(x)
    # def _predict_hidden(self, x):
    #     ans = [n.predict(x) for n in self._hidden]
    #     return np.array(ans)
    #
    # def _predict_output(self, y_hidden):
    #     ans = [n.predict(y_hidden) for n in self._output]
    #     return np.array(ans)
    #
    # def _update_output(self, prior_output, truth, output):
    #     g = [n.learn(prior_output, truth, output) for n in self._output]
    #     return np.array(g)
    #
    # def _calc_hidden_gradient(self, neurons, output, subsequent_neurons):
    #     g = np.zeros(len(neurons))
    #     for i in range(len(neurons)):
    #         n = neurons[i]
    #         g[i] = np.sum([x.get_weight(i) * x.gradient for x in subsequent_neurons])
    #     g *= output * (1 - output)
    #     return g
    #
    # def _update_hidden( # def feed(self, x, y):
    #     x = np.array(x)
    #     y = np.array(y)
    #     hidden_output = self._predict_hidden(x)
    #     final_output = self._predict_output(hidden_output)
    #     self._update_output(hidden_output, y, final_output)
    #     hidden_gradient = self._calc_hidden_gradient(self._hidden, hidden_output, self._output)
    #     self._update_hidden(x, self._hidden, hidden_gradient)
    #
    # def predict(self, x):
    #     pass
    #
    # def size(self):
    #     return {
    #         "input": self._n,
    #         "hidden": self._n_hidden,
    #         "output": self._n_output
    #     }self, inputs, neurons, gradients):
    #     for n, g in zip(neurons, gradients):
    #         n.learn(inputs, g=g)


def test():
    b = BPPerceptron(2, 1, 1)
    x = np.array([
            [0, 0], [0, 1], [1, 0], [1, 1]
        ])
    y = np.array([
        [0], [1], [1], [0]
    ])

    b.train_many( x=x.repeat(10, 0), y=y.repeat(10, 0))
    ans = b.predict([1, 1])
    print(ans)
# TODO: early stopping
# TODO: regularization

if __name__ == "__main__":
    test()