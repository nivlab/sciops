data {

    // Metadata
    int  N;
    int  K;
    int  T;
    
    // Data
    int<lower=1, upper=4>  Y[N,T];
    
    // Mappings
    vector<lower=0,upper=1>[N]  reject_ix; 
    int<lower=1, upper=K>       scale_ix[T];

}
transformed data {

    // Ordinal thresholds
    vector[3] thresh = [1.5, 2.5, 3.5]'; 

}
parameters {

    // Subject-level parameters
    matrix[K,N]  theta;
    vector[N]    alpha;
    
    // Item-level parameters
    vector[T]    beta;
    vector<lower=0>[T] sigma;

}
model {

    // Priors
    to_vector(theta) ~ normal(0, 2);
    alpha ~ normal(0, 2);
    beta ~ normal(0, 2);
    sigma ~ normal(0, 2);
    
    // Main loop
    for (i in 1:N) {
    
        for (j in 1:T) {
        
            real mu = alpha[i] + beta[j] + theta[scale_ix[j],i];
        
            if ( Y[i,j] == 1 ) {
                real p = inv_logit( (thresh[Y[i,j]] - mu) / sigma[j] ) - 0;
                target += log(p);
                
            } else if ( Y[i,j] == 4 ) {
                real p = 1 - inv_logit( (thresh[Y[i,j]-1] - mu) / sigma[j] );
                target += log(p);
                
            } else {
                real p = inv_logit( (thresh[Y[i,j]] - mu) / sigma[j] ) - inv_logit( (thresh[Y[i,j]-1] - mu) / sigma[j] );
                target += log(p);
            }
            
        }
    
    }

}
generated quantities {

    vector[3] contrasts;
    contrasts[1] = sum( (1-reject_ix) .* alpha ) / sum(1-reject_ix);
    contrasts[2] = sum( reject_ix .* alpha ) / sum(reject_ix);
    contrasts[3] = contrasts[1] - contrasts[2];
    
}