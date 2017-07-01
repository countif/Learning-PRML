import numpy as np
from math import gamma
from scipy.special import gammaln
from scipy.stats import multivariate_normal, wishart

from Probabilistic.GMM import GMM, rand_positive


class Gibbs:
    def __init__(self, k, dim, data):
        self.k = k
        self.dim = dim
        self.data = np.array(data)
        assert data.shape[1] == dim
        self.n = len(data)

        self.a = 1.0                # TODO: setting
        self.a0 = self.a
        self.ak = self.a0 / self.k
        self.k0 = 10.0               # TODO: ?
        self.kn = self.k0 + self.n
        self.v0 = dim + 10             # (v0 > dim + 1)must holds
        # self.m0 = np.ones(dim)     # TODO: check
        self.m0 = np.sum(data, 0)
        self.s0 = np.cov(data.T)

        self.z = np.random.randint(0, k, size=self.n)
        self.freq = np.bincount(self.z)

    def _cov(self, data):
        ret = np.zeros((self.dim, self.dim))
        for d in data:
            ret += np.dot(d.reshape((self.dim, 1)), d.reshape((1, self.dim)))
        return ret

    def _cov_single(self, data):
        return np.dot(data.reshape((self.dim, 1)), data.reshape((1, self.dim)))

    def _term1(self, omit):
        """
        term1 in Gibbs sampling is $P(z_i=k | z_{\i}, \alpha)$
        """
        self.freq[self.z[omit]] -= 1
        ret = (self.freq + self.ak) / (self.n + self.a0 - 1)
        self.freq[self.z[omit]] += 1
        return ret

    def _term2(self, k, x_star):
        """
        term2 in Gibbs sampling is $p(x_i | x_{k\i}, \beta)$
        """
        index = np.where(self.z == k)[0]
        if len(index) == 0:
            return 0
        data = self.data[index]
        n = data.shape[0]
        kn = self.k0 + n
        vn = self.v0 + n

        data_cov = self._cov(data)
        data_mean = np.mean(data, 0)
        data_mean_star = (np.mean(data, 0) * n + x_star) / (n + 1)
        mn = (self.k0 * self.m0 + n * data_mean) / kn
        mn_star = (self.k0 * self.m0 + (n + 1) * data_mean_star) / kn
        sn = self.s0 + data_cov + self.k0 * self._cov_single(self.m0) + kn * self._cov_single(mn)
        sn_star = self.s0 + data_cov + self._cov_single(x_star) + self.k0 * self._cov_single(self.m0) + (kn + 1) * self._cov_single(mn_star)

        numerator1 = np.power(np.pi * (kn + 1) / kn, -self.dim / 2.0)
        temp = np.linalg.det(sn_star)
        numerator2 = np.power(temp / np.linalg.det(sn), -vn / 2.0) * np.power(temp, -0.5)
        numerator3 = np.exp(gammaln((vn + 1) / 2.0) - gammaln((vn + 1 - self.dim) / 2.0))
        ret = numerator1 * numerator2 * numerator3

        return ret

    # def _form_dist(self):
    #     mu = np.zeros((self.dim, self.k))
    #     sigma = np.zeros((self.dim, self.dim, self.k))
    #     pi = np.zeros(self.k)
    #     for i in range(self.k):
    #         c = self.data[self.z == i]
    #         pi[i] = (len(c) / float(self.n))
    #         mu[:, i] = c.mean(0)
    #         sigma[:, :, i] = np.cov(c, rowvar=False)
    #     return np.array(mu), np.array(sigma), np.array(pi)

    def _form_dist(self):
        mu = np.zeros((self.dim, self.k))
        sigma = np.zeros((self.dim, self.dim, self.k))
        _pi = np.bincount(self.z) / float(self.n)
        pi = np.zeros(self.k)
        pi[:len(_pi)] = _pi
        for i in range(self.k):
            mu[:, i], sigma[:, :, i] = self._update_component(i)
        return mu, sigma, pi

    def _update_component(self, i):
        index = self.z == i
        data = self.data[index]
        s = len(data)
        if s == 0:
            sigma = wishart.rvs(df=self.dim, scale=np.linalg.inv(self.s0))
            mu = np.random.multivariate_normal(self.m0, sigma)
        else:
            data_sum = data.sum(0)
            data_mean = data_sum / s

            b_term = self._cov(data - data_mean)
            m_dash = (self.k0 * self.m0 + data_sum) / (s + self.k0)
            # c_dash = s + 0.1
            a_dash = s + self.dim
            b_dash = self.s0 + b_term + s / (self.dim * s + 1) * self._cov_single(data_mean - self.m0)

            sigma = wishart.rvs(df=a_dash, scale=np.linalg.inv(b_dash))
            if self.dim > 1:
                mu = np.random.multivariate_normal(m_dash, sigma)
            else:
                mu = np.random.normal(m_dash, sigma)
        return mu, sigma

    def test(self):
        mu, sigma, pi = self._form_dist()
        self.log_likelihood(mu, sigma, pi)

    def fit_and_test(self, max_iter):
        for _iter in range(max_iter):
            if _iter % 2 == 0:
                print(self._form_dist())
                # print(_iter)
                # self.test(mu_t, sigma_t, pi_t)

            for i in range(self.n):
                t1 = self._term1(i)

                t2 = np.zeros(self.k)
                last = self.z[i]
                self.freq[last] -= 1
                self.z[i] = -1
                for k in range(self.k):
                    t2[k] = self._term2(k, self.data[i])
                cum = np.cumsum(t1 * t2)
                cum /= cum[-1]

                k_new = np.where(np.random.random() < cum)[0][0]
                self.z[i] = k_new
                self.freq[k_new] += 1
            print(self.freq)

    def predict(self):
        return self._form_dist()

    def log_likelihood(self, mu, sigma, pi):
        # mu, sigma, pi = self._form_dist()
        mat = np.zeros((self.n, self.k))
        for i in range(self.k):
            dist = multivariate_normal(mu[:, i], sigma[:, :, i])
            for j in range(self.n):
                mat[j, i] = dist.pdf(self.data[j])
        evaluation = np.sum(np.log(np.dot(mat, pi)))
        print(evaluation)


def test():
    g = GMM(2, 1, a=[0.5, 0.5], mu=[[-2., 2.]], sigma=[[[.3, .3]]])
    data = g.observe(20000)
    data.tofile('Probabilistic/tmp/gibbs/data.txt', sep=' ')
    plt = g.plot()
    gb = Gibbs(2, 1, data[:1000])
    # print('Target log-likelihood')
    # gb.log_likelihood(g.mu, g.sigma, g.a)

    gb.fit_and_test(100)
    mu, sigma, a = gb.predict()


if __name__ == '__main__':
    test()


