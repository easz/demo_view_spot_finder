# View Spot Finder

## Requirement

Install Python3 (e.g. with [conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-python.html))

Install necessary python requirements:

~~~
pip install -r requirements.txt
~~~

(Optional) Install serverless:

~~~
npm install -g serverless
~~~

## Quick Start


Find `5` top vew spots from the landscape scene defined in `data/mesh.json`:

~~~
python view_spot_finder.py data/mesh.json 5
~~~

(Optional) do the same thing by running serverless AWS Lambda locally:

~~~
serverless invoke local --function find_spot --path testdata/mesh_200_spot_5.json
~~~

or check out this [notebook](sandbox.ipynb) to have an overview.

## Detail

The structure of input data for the AWS Lamda function:

~~~
{
  N: <number value>,
  mesh: {
    nodes: [
      { id: <node_id>, x: <number value>, y: <number value> },
      ...
    ],
    elements: [
      { id: <element_id>, nodes: [ <node_id>, <node_id>, <node_id> ] },
      ...
    ],
    values: [
      { element_id: <element_id>, value: <number value>},
      ...
    ]
  }
}
~~~

where `N` is the number of view spots and `mesh` defines a hilly landscape.

## Strategy

Either a generic solution or an optimized one with assumptions:

 - a generic solution can work with any unstructured mesh.
   - which can involve nearest neighbor lookup like KDTree
 - or an optimized solution if the landscape scene can be represneted in a rigid grid
   - actually it makes sense to have structured mesh or grid for a geo-spatial application. (e.g. with raster coordinate)

In this demo a well-defined mesh is at first converted to a 2d grid where mesh elements also get down sampling.
Then, a local maximum filter is applied on such 2d grid data and peaks can be found quickly.
Finally the actual elements from the original mesh will be retrieved according to those peaks found in the grid.

Depending on the resolution of a landscape "map" as well as the geographical characteristics (e.g. size of a hill), we can apply further down-sampling or approximation to further accelerate the calculation. A divide and conquer strategy can also be apply to handle large dataset.
