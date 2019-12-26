# Maximum Cap Search
A repository containing scripts for finding maximum caps by Jaron Wang with guidance from [Professor Robert Won](https://faculty.washington.edu/robwon/index.html) for the WXML group "The Card Game Set and Affine Geometry" Fall Quarter 2019.

More information on caps can be found [[here](https://arxiv.org/abs/1809.05117)]. 
A more intuitive view on affine geometry in terms of the card game set can be found [[here](https://homepages.warwick.ac.uk/staff/D.Maclagan/papers/set.pdf)].

Note: In this repository, I refer to a cap in which no point can be added without invalidating the cap as maximal, and a cap of largest cardinal size to be a maximum cap. In the other literature, the first is referred to as complete and maximal respectively. This is because I think that maximal and maximum are more common terminology in math.

## Algorithms
### Cap Validation Search
This is a preliminary naive search which was the first way written. The pseudocode is as follows:
```
Start with some cap.
For each of the points not in the cap:
    check if the point added would cause the collection to not be cap
    if it is a valid cap:
      recurse with the new cap
return the largest cap found this way
```
This is clearly not very optimized as it will end up checking a lot of elements of the power set of the points, so after the initial version was written no updates have been made. However, further upon further thought, if there is a clear estimation of the size of the maximum cap, then a variant of this could potentially be used with some sort of bisection search. Currently unsure if this is better than the other method, but I think it has potential as evaluation is fairly cheap.

### Flat Elimination Search
Instead of searching all the points, we instead keep an invariant that all the set of points to potentially added always contain the points which will not invalidate the cap. To do this, we perform something called flat-elimination. The pseudocode now looks like such:

```
Start with a valid cap and its corresponding validset which is accurate.
for each point in validset:
    newcap <- cap + point
    update validset of newcap
    recurse
return the largest cap found this way
```

This does better in a more powerful computer as the the update validset part of this algorithm is highly parallelizable as each flat can be eliminated in parallel and doesn't need to be lock-safe.

## Data Format
The results from these algorithm are found in ./results/ and are of the format d_q_n.dat and d_q_n_all.dat . The former contains just one maximum cap and the latter contains all of the maximum caps. In addition, there is a visualizer.py file for outputing a png for each 
cap. The visualizer.py looks for the data files in the results to do so. Example outputs:

## Running the Code
### flat-elim-search.py
Two possible arguments
```py flat-elim-search.py d q n```
This runs the search for a d-cap in F_q^n.
```py flat-elim-search.py n```
This finds all d-caps in F_3^n for d in [1,n].
You can also specify n <= 0, and it will do this for all n until terminated.

Running in debug mode forces a search to be done and records the time in ms it takes to complete. Otherwise, it will just use a previously found result if it exists. 
### cap-val-search.py
Currently variable d is not supported. Windows:
```py ./cap-val-search.py q n```
Example: (finds a 1-cap in F_3^5)
```py ./cap-val-search.py 3 5```
Running it with the debug flag (-O) causes all the caps it iterates to be written to a debug file. 

### visualizer.py
```py ./cap-val-search.py d q n```
```py ./cap-val-search.py q n```

## Known Issues
- [ ] While the parameter q is a parameter in all the files given, changing this parameter to a value which is not 3 is currently not supported. (in contexts where d and n are also specified). This is partially due to the fact that we are only in a field for certain values of q.
- [ ] The visualizer is always left upper justified. 
- [ ] For large enough spaces, the visualizer line width becomes 0 and crashes.
