# What's in this file

The purpose of this document is to collect the functionality of each library in this package. Please consult README.md for basic functionality.

## Interval_Matrix_Algebra_Calculator_v0.py

*Is this really version 0 at this point?*

Interval Matrix Algebra Calculator contains essential functions, including importing a *csv* file, arithmetic, and visualization options. **In a future refactor, visualization will be built into its own library.**

### Functions

#### soapConverter(path)

Takes a *csv* file generated from SOAP and returns a workable TVG matrix.

#### csvs_in_folder(folder)

Returns a list of csv files relative to top directory

#### interval_matrix_mult(X, Y)

Performs tropical multiplication on two TVG matrices.

#### interval_matrix_sum(X, Y)

Performs tropical addition on two TVG matrices.

#### remove_diagonal(A)

Zeros out the diagonal of a TVG matrix. The authors of this library have found this to be useful to declutter a matrix when passing it to a visualization function. Additionally, interesting behavior arises in the *k-walks* when looking at the "non-trivial" k-walks.

#### matrix_k_walk(A, k)

Returns $ A^k $.

#### A_star(A)

Returns $ A^\* $, the Kleene-Star of the TVG matrix. This is equivalent to the sum of all possible walks of the matrix.

#### A_star_r(A, r)

Returns the partial Kleene-Star -- that is, the sum of k-walks up to r-walks.

#### get_length(intervals, min, max)

Returns the length of a union of intervals, using min and max as bounds.

#### connection_barcode(A, i, j, n)

Creates a visual barcode out of the specific k-walks the $ i,j^{th} $ entry of A. That is, it shows the intervals for 1-walks, 2-walks, ..., up to n-walks.

#### matrix_nontrivial_k_walk(A, k)

Equivalent to *matrix_k_walk(remove_diagonal(A), k)*. This was meant to write cleaner code, although it is largely redundant.

#### matrix_barcode_3d_inline(M)

Opens a scalable, saveable 3D graph of the barcode of the matrix M.

#### matrix_barcode_3d(M, n)

Saves to the root directory 3D graphs of the barcodes for each k-walk from 1 to n.


