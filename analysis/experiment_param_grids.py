from sklearn.gaussian_process.kernels import RBF, DotProduct, Matern, RationalQuadratic, WhiteKernel


names = [
    "Nearest Neighbors",
    "Linear SVM",
    "RBF SVM",
    "Gaussian Process",
    "Decision Tree",
    "Random Forest",
    "Neural Net",
    "AdaBoost",
    "Naive Bayes",
    "QDA",
]
knn = dict(
    leaf_size=list(range(1, 15)),
    n_neighbors=list(range(1, 10)),
    p=[1, 2]
)

gaussian_process = dict(
    kernel=[1*RBF(), 1*DotProduct(), 1*Matern(),  1*RationalQuadratic(), 1*WhiteKernel()]
)

decision_tree = dict(
    criterion=['gini', 'entropy'],
    max_depth=list(range(1, 10)),
    min_samples_split=list(range(1, 10)),
    min_samples_leaf=list(range(1, 10))
)

hyperparameters: dict[str, dict] = {
    "Nearest Neighbors": knn,
    "Gaussian Process": gaussian_process,
    "Decision Tree": decision_tree
}