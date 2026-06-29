"""
Manifold-learning utilities for exploring sampled parameter spaces.

These methods operate on completed simulation samples. They do not run
new model evaluations.
"""

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import umap


def get_parameter_matrix(samples: pd.DataFrame, parameter_names: list[str]):
    """Extract and standardize selected parameter columns."""
    parameter_values = samples[parameter_names].copy()

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(parameter_values)

    return scaled_values


def run_pca_projection(samples, parameter_names, n_components=2):
    """Run PCA on selected parameter columns."""
    x_scaled = get_parameter_matrix(samples, parameter_names)

    model = PCA(n_components=n_components)
    embedding = model.fit_transform(x_scaled)

    embedding_df = pd.DataFrame(
        embedding,
        columns=[f"Dim{i + 1}" for i in range(n_components)],
        index=samples.index,
    )

    embedding_df["QoI"] = samples["QoI"].values

    loadings = pd.DataFrame(
        model.components_.T,
        columns=[f"Dim{i + 1}" for i in range(n_components)],
        index=parameter_names,
    )

    explained_variance = pd.DataFrame({
        "component": [f"Dim{i + 1}" for i in range(n_components)],
        "explained_variance_ratio": model.explained_variance_ratio_,
    })

    return embedding_df, loadings, explained_variance


def run_tsne_projection(
    samples,
    parameter_names,
    n_components=2,
    perplexity=30,
    random_state=1,
):
    """Run t-SNE on selected parameter columns."""
    x_scaled = get_parameter_matrix(samples, parameter_names)

    model = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        random_state=random_state,
        init="pca",
        learning_rate="auto",
    )

    embedding = model.fit_transform(x_scaled)

    embedding_df = pd.DataFrame(
        embedding,
        columns=[f"Dim{i + 1}" for i in range(n_components)],
        index=samples.index,
    )

    embedding_df["QoI"] = samples["QoI"].values

    return embedding_df, None, None


def run_umap_projection(
    samples,
    parameter_names,
    n_components=2,
    n_neighbors=15,
    min_dist=0.1,
    random_state=1,
):
    """Run UMAP on selected parameter columns."""
    x_scaled = get_parameter_matrix(samples, parameter_names)

    model = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        random_state=random_state,
    )

    embedding = model.fit_transform(x_scaled)

    embedding_df = pd.DataFrame(
        embedding,
        columns=[f"Dim{i + 1}" for i in range(n_components)],
        index=samples.index,
    )

    embedding_df["QoI"] = samples["QoI"].values

    return embedding_df, None, None


def run_active_subspace_placeholder(samples, parameter_names):
    """
    Placeholder for future active-subspace implementation.

    True active subspaces require gradients of QoI with respect to parameters.
    We will add this once UQdash has a gradient/finite-difference interface.
    """
    raise NotImplementedError(
        "Active Subspaces require gradients or finite-difference model "
        "evaluations. This will be added in a later version."
    )


def run_manifold_projection(method, samples, parameter_names, random_state=1):
    """Dispatch dimensionality-reduction method."""
    if method == "PCA":
        return run_pca_projection(samples, parameter_names)

    if method == "t-SNE":
        return run_tsne_projection(
            samples,
            parameter_names,
            random_state=random_state,
        )

    if method == "UMAP":
        return run_umap_projection(
            samples,
            parameter_names,
            random_state=random_state,
        )

    if method == "Active Subspaces":
        return run_active_subspace_placeholder(samples, parameter_names)

    raise ValueError(f"Unsupported manifold method: {method}")