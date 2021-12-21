import numpy as np


def drop_highly_correlated_features(matrix):
    """drop high correlation features

    Parameters
    ----------
    matrix_of_term_freq : pandas.DataFrame
        The matrix with term frequency

    Returns
    -------
    pandas.DataFrame
        the reduced matrix without higly correlated features
    """

    # Create correlation matrix
    corr_matrix = matrix.corr().abs()

    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))

    # Find index of feature columns with correlation greater than 0.95
    to_drop = [column for column in upper.columns if any(upper[column] > 0.95)]

    return matrix.drop(columns=to_drop)

