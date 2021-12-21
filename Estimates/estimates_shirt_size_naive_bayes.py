import pandas as pd
from collections import Counter
from sklearn import preprocessing
from sklearn.linear_model import LassoCV
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_selection import RFECV

from utils.data_cleanup import *


def main():
    data = pd.read_csv("./data/processed_data.csv", index_col=0)
    target = pd.read_csv("./data/processed_target_data.csv", index_col=0)

    data_clean = data.drop(columns=['doc_key'])
    data_clean.fillna(0, inplace=True)

    target_clean = target.drop(columns=['doc_key'])
    target_clean.fillna(0, inplace=True)


    # Data Extraction
    X = data_clean.drop(columns=['estimate'])
    y = data_clean['estimate']

    bin_labels_2 = ['S', 'L']
    bin_labels_3 = ['S', 'M', 'L']
    bin_labels_4 = ['S', 'M', 'L', 'XL']
    bin_labels_5 = ['XS', 'S', 'M', 'L', 'XL']

    bin_labels = bin_labels_4
    y_bins = pd.qcut(y, q=len(bin_labels), labels=bin_labels)
    raw_bins = pd.qcut(y, q=len(bin_labels))

    X = drop_highly_correlated_features(X)

    from sklearn.model_selection import LeaveOneOut, ShuffleSplit, StratifiedShuffleSplit

    X_train, X_test, y_train, y_test = train_test_split(X, y_bins, test_size=0.05)

    model_cv = LeaveOneOut()
    model = MultinomialNB()
    selector = RFECV(estimator=model, min_features_to_select=10, step=1, cv=model_cv, scoring='accuracy')
    selector = selector.fit(X_train, y_train)
    y_pred = selector.predict(X_test)


    print("=== Results with Multinomial Naive Bayes ===")
    print('Bins: ', bin_labels)
    print('Bin Ranges: ', raw_bins.dtype.categories.to_tuples().to_numpy())
    print('Counts (training set):')
    print(y_train.value_counts())

    print('\nTotal number of features (aka Words) in data: %d' % (data_clean.shape[1]-1))
    print('Total number of uncorrelated features (aka Words) in data: %d' % X.shape[1])
    print("Number of features (aka Words) in optimal model: %d" % selector.n_features_)

    print("\nTest doc: %s" % data.loc[list(X_test.index)[0]]['doc_key'])
    print("Expected vs Predicted Size: {} vs {}".format(y_test.iloc[0], y_pred[0]))
    print("Class Probabilities: ", selector.classes_, selector.predict_proba(X_test))

    plot_rfecv_selection(selector)


def plot_rfecv_selection(rfecv):
    plt.figure(figsize=(16, 9))
    plt.title('Recursive Feature Elimination with Cross-Validation', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Number of features selected', fontsize=14, labelpad=20)
    plt.ylabel('% Correct Classification', fontsize=14, labelpad=20)
    plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_, color='#303F9F', linewidth=3)

    plt.savefig('RFECV_Selection.png')


def compute_tf_idf(matrix_of_term_freq):
    """Computes the tf_idf matrix from a term frequency matrix

    Parameters
    ----------
    matrix_of_term_freq : pandas.DataFrame
        The matrix with term frequency

    Returns
    -------
    pandas.DataFrame
        the TF-IDF matrix for the input matrix with the same columns
    """
    from sklearn.feature_extraction.text import TfidfTransformer

    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer = tfidf_transformer.fit_transform(matrix_of_term_freq)
    X = pd.DataFrame(tfidf_transformer.toarray(), columns=matrix_of_term_freq.columns)
    return X


if __name__ == "__main__":
    main()