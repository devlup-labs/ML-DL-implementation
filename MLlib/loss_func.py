import numpy as np
from MLlib.activations import Sigmoid
from MLlib import Tensor
from MLlib import autograd
from MLlib.utils.misc_utils import unbroadcast


class MeanSquaredError(autograd.Function):
    """
    Calculate Mean Squared Error.
    """

    __slots__ = ()

    @staticmethod
    def forward(ctx, prediction, target):
        if not (type(prediction).__name__ == 'Tensor' and
                type(target).__name__ == 'Tensor'):

            raise RuntimeError("Expected Tensors, got {} and {}. Please use "
                               ".loss() method for non-Tensor data"
                               .format(type(prediction).__name__,
                                       type(target).__name__))

        requires_grad = prediction.requires_grad

        batch_size = target.data.shape[0]

        out = prediction.data - target.data

        if requires_grad:
            ctx.derivative_core = out

        out = np.sum(np.power(out, 2)) / (2*batch_size)

        output = Tensor(out, requires_grad=requires_grad,
                        is_leaf=not requires_grad)

        return output

    @staticmethod
    def backward(ctx, grad_output):
        derivative = ctx.derivative_core

        grad_prediction = (derivative / derivative.shape[0]) * grad_output.data

        return Tensor(unbroadcast(grad_prediction, derivative.shape))

    @staticmethod
    def loss(X, Y, W):
        """
        Calculate loss by mean square method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector
        W:ndarray(dtype=float)
          Weights

         RETURNS
         =======

         array of mean squared losses
        """
        M = X.shape[0]
        return np.sum((np.dot(X, W).T - Y) ** 2) / (2 * M)

    @staticmethod
    def derivative(X, Y, W):
        """
        Calculate derivative for mean square method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector
        W:ndarray(dtype=float)
          Weights

         RETURNS
         =======

         array of derivates
        """
        M = X.shape[0]
        return np.dot((np.dot(X, W).T - Y), X).T / M


class MSELoss(MeanSquaredError):
    pass


class LogarithmicError():
    """
    Calculate Logarithmic Error.
    """

    @staticmethod
    def loss(X, Y, W):
        """
        Calculate loss by logarithmic error method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector
        W:ndarray(dtype=float)
          Weights

         RETURNS
         =======

         array of logarithmic losses
        """
        M = X.shape[0]
        sigmoid = Sigmoid()
        H = sigmoid.activation(np.dot(X, W).T)
        return (1/M)*(np.sum((-Y)*np.log(H)-(1-Y)*np.log(1-H)))

    @staticmethod
    def derivative(X, Y, W):
        """
        Calculate derivative for logarithmic error method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector
        W:ndarray(dtype=float)
          Weights

         RETURNS
         =======

         array of derivates
        """
        M = X.shape[0]
        sigmoid = Sigmoid()
        H = sigmoid.activation(np.dot(X, W).T)
        return (1/M)*(np.dot(X.T, (H-Y).T))


class AbsoluteError():
    """
    Calculate Absolute Error.
    """

    @staticmethod
    def loss(X, Y, W):
        """
        Calculate loss by absolute error method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector
        W:ndarray(dtype=float)
          Weights

         RETURNS
         =======

         array of absolute losses
        """
        M = X.shape[0]
        return np.sum(np.absolute(np.dot(X, W).T - Y)) / M

    @staticmethod
    def derivative(X, Y, W):
        """
        Calculate derivative for absolute error method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector
        W:ndarray(dtype=float)
          Weights

         RETURNS
         =======

         array of derivates
        """
        M = X.shape[0]
        AbsError = (np.dot(X, W).T-Y)
        return np.dot(
            np.divide(
                AbsError,
                np.absolute(AbsError),
                out=np.zeros_like(AbsError),
                where=(np.absolute(AbsError)) != 0),
            X
        ).T/M


class CosineSimilarity():
    """
    Calculate Similarity between actual value and similarity value.
    """

    @staticmethod
    def loss(X, Y, W):
        """
        Calculate error by cosine similarity method

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector
        W:ndarray(dtype=float)
          Weights

         RETURNS
         =======

         Percentage of error in the actural value and predicted value
         """
        sigmoid = Sigmoid()
        H = sigmoid.activation(np.dot(X, W).T)
        DP = np.sum(np.dot(H, Y))
        S = DP/((np.sum(np.square(H))**(0.5))*(np.sum(np.square(Y))**(0.5)))
        dissimilarity = 1-S
        return dissimilarity*(np.sum(np.square(Y))**(0.5))


class Log_cosh():

    @staticmethod
    def logcosh_loss(X, Y):
        """
        Calculate Error by log cosh method

        PARAMETERS
        ==========

        X: ndarray(dtype=float,ndim=1)
           Actual values
        Y: ndarray (dtpye=float,ndim=1)
           Predicted values

        RETURNS
        =======

        Logarithm of the hyperbolic cosine of the prediction error
        """
        p = np.cosh(Y - X)
        loss = np.log(p)
        error = np.sum(loss)
        return error

    @staticmethod
    def derivative_logcosh(X, Y):
        """
        Calculate the derivative of "log cosh" loss method

        PARAMETERS
        ==========

        X: ndarray(dtype=float,ndim=1)
           Actual values
        Y: ndarray (dtpye=float,ndim=1)
           Predicted values

           RETURNS
           =======

           Derivative of Log cosh prediction error
           """
        t = np.tanh(Y-X)
        derivative = np.sum(t)
        return derivative


class Huber():
    """
    Calculate Huber loss.
    """

    @staticmethod
    def loss(X, Y, delta=1.0):

        """
        Calculate loss by Huber method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector

         RETURNS
         =======

         array of Huber losses
        """
        return np.where(np.abs(X-Y) <= delta,
                        0.5*(X-Y)**2,
                        delta*(np.abs(X-Y)-0.5*delta))

    @staticmethod
    def derivative(X, Y, delta=1.0):

        """
        Calculate derivative for Huber method.

        PARAMETERS
        ==========

        X:ndarray(dtype=float,ndim=1)
          input vector
        Y:ndarray(dtype=float)
          output vector

         RETURNS
         =======

         array of derivates
        """

        return np.where(np.abs(X - Y) <= delta, X - Y, delta * np.sign(X - Y))


class MeanSquaredLogLoss():
    """""
    Calcute Mean Squared Log Loss
    """

    @staticmethod
    def loss(X, Y, W):
        """
            Calculate  Mean Squared Log Loss

            PARAMETERS
            ==========

            X:ndarray(dtype=float,ndim=1)
              input vector
            Y:ndarray(dtype=float)
              output vector
            W:ndarray(dtype=float)
              Weights

            RETURNS
            =======

            array of mean of logarithmic losses
        """

        M = X.shape[0]
        sigmoid = Sigmoid()
        H = sigmoid.activations(np.dot(X, W).T)
        return np.sqrt((1 / M) * (np.sum(np.log(Y + 1) - np.log(H + 1))))
