<center>
# Expectation Maximization
> Ch.9 *Methods for statistical learning*, H. Li
</center>  

Iterative algorithm EM use E step and M step to infer probabilistic model with hidden variables. 

# 9.1 EM Algorithm
From model $\theta$ emerges observed variable Y and unobserved variable Z, s.t. likelihood function of observed variable is
$$P(Y|\theta)=\sum_zP(Z|\theta)P(Y|Z,\theta)=\prod_j(\sum_z P(Z|\theta)P(y_j|Z, \theta))$$
We maximize $$\hat{\theta}=\arg\max_\theta\log P(Y|\theta)$$
Further, Y is incomplete-data while (Y,Z) is complete data. Given observation Y, its probabilistic distribution is $P(Y|\theta)$, which is also the likelihood function of incomplete-data Y. We take log likelihood function of incomplete data $L(\theta)=\log P(Y|\theta)$, and $\log P(Y,Z|\theta)$ for complete data.

EM algorithm iterates to infer maximum likelihood estimate on $L(\theta)$.

Input:

- Y, Z
- Joint probability distribution $P(Y,Z|\theta)$
- Conditional probability distribution $P(Z|Y,\theta)$

Output: 

- $\theta$

Steps:

1. choose $\theta^{(0)}$
2. E step: with $\theta^{(i)}$, calculate $$Q(\theta, \theta^{(i)})=E_z[\log(P(Y,Z|\theta)|Y,\theta^{(i)})]$$
$$=\sum_z\log P(Y,Z|\theta)P(Z|Y,\theta^{(i)})$$
3. M step: $$\theta^{(i+1)}=\arg\max_\theta Q(\theta, \theta^{(i)})$$
4. Repeat until converge

> Notes:  
> 1. EM is sensitive to initial value.  
> 2. $Q(\theta, \theta^{(i)})$ takes first argument as variable to be maximized and second as current estimate.  
> 3. Iterative steps are proved to increase $L(\theta)$ or reach at local optimal.  
> 4. A common stopping condition is $||\theta^{(i+1)} - \theta^{(i)}||<\epsilon$ or $||Q(\theta, \theta^{(i+1)})-Q(\theta, \theta^{(i)})||<\epsilon$  
> 5. Without digging deep into the proof, we should know that iteration is pushing the lower bound of the L to find the maximum.


# 9.3 EM algorithm for Gaussian mixture model (GMM)
GMM is defined as $$P(y|\theta)=\sum_k\alpha_k\phi(y|\theta_k), \ \ \theta_k=(\mu_k,\sigma^2_k)$$
We can observe $y_j$ generated by GMM, and hidden variable $\gamma_{jk}$ is set to 1 when the j-th observation comes from sub-model k.
$$P(y,\gamma|\theta)=\prod_jP(y_j,\gamma_{j1}, ..., \gamma_{jK}|\theta)$$
$$=\prod_k\alpha_k^{n_k}\prod_j[\phi(y_j|\theta_j)]^{\gamma_{jk}}$$
where 
$$n_k=\sum_j\gamma_{jk}, \sum_k n_k=N$$

> some proof here

1. set initial variable
2. E step: calculate responsiveness on $y_j$ of model k 
    $$\hat\gamma_{jk}=\frac{\alpha_k\phi(y_j|\theta_k)}{\sum_k\alpha_k\phi(y_j|\theta_k)}$$
3. M step: update 
    $$\hat\mu_k=\frac{\sum_j\hat\gamma_{jk}y_j}{\sum_j\hat\gamma_{jk}}$$
    $$\hat\sigma_k^2=\frac{\sum\hat\gamma_{jk}(y_j-\mu_k)^2}{\sum\hat\gamma_{jk}}$$
    $$\alpha_k=\frac{\sum_j\hat\gamma_{jk}}{N}$$
4. Iterate till converge



---
# Gibbs Sampler for GMM
For mathematical convenience, we assume
$$c_i|\vec{\pi}\sim\rm{Discrete}(\vec{\pi})\ \ \ \rm{ or\ } P(c_i=k)=\pi_k$$
$$\vec{y_i}|c_i=k;\Theta\sim\rm{Gaussian}(\cdot|\theta_k)$$
$$\vec{\pi}|\alpha \sim \rm{Dirichlet}(\cdot | \frac{\alpha_i}{K},... )$$
$$\Theta\sim\cal{G}_0$$
> $$\rm{Dirichlet}(x)=\frac{1}{B(\alpha)}\prod_i x_i^{\alpha_i-1}$$  
> $\cal{G}_O$ is shorthand of  
> $$\Sigma_k\sim\rm{Inverse-Wishart}_{v_0}(\Lambda_0^{-1})$$
> $$\vec{\mu}_k\sim\rm{Gaussian}(\vec{\mu}_0,\Sigma_k/\kappa_0)$$
> 




