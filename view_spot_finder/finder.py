import numpy as np
from scipy.ndimage import maximum_filter
from operator import itemgetter

# implementation with pure functional procedure
# it could be refactored as object-oriented way....

def find_spot(mesh, N):
  """ find view spots in a landscape """
  try:
    validate_mesh_grid(mesh)
    grid = scale_to_grid(mesh)
    peaks = find_peak(grid)

    elements = []
    for peak in peaks:
      idx = lookup_mesh_element(grid=grid, gcoord=peak, mesh=mesh)
      values = list(itemgetter(*idx)(mesh['values']))
      elements.append(max(values, key=lambda v: v['value']))
    elements.sort(key=lambda v: v['value'], reverse=True)
    return elements[0:N]
  except AssertionError:
    raise RuntimeError("Support only well-defined mesh format (i.e. implicit grid)")

def find_peak(grid):
  """
    find peak (e.g local maxima) in a 2d grid
    @param grid
            a 2d grid structure
    @return a list of [x, y] pair where x,y denote the index from the grid
            For example: [[x_0, y_0], [x_1, y_1], ... [x_k, y_k]]
  """
  local_max = maximum_filter(grid, size=(4,4), mode="nearest") == grid
  return np.swapaxes(np.nonzero(local_max), 0, 1)

def validate_mesh_grid(mesh):
  """
    validate if a mesh object is in a well-defined format.
    A well-defined mesh has implicit a grid structure.
    An AssertionError would be raised on an invalidation.
    @param mesh
            a well-defined mesh object
  """
  elements = mesh['elements']
  nodes = mesh['nodes']
  values = mesh['values']
  # all are sorted w.r.t array index
  for idx, n in enumerate(nodes):
    assert n["id"] == idx
  for idx, e in enumerate(elements):
    assert e["id"] == idx
  for idx, v in enumerate(values):
    assert v["element_id"] == idx
  # triangle elements are well defined
  assert len(elements) == len(values)
  # referenced nodes of triangle are well defined
  ref_n = {n for e in elements for n in e["nodes"]}
  assert len(ref_n) == len(nodes)
  # two consecutive elements share a long edge
  assert len(elements) % 2 == 0
  for idx in range(0, len(elements), 2):
    e1 = set(elements[idx]['nodes'])
    e2 = set(elements[idx+1]['nodes'])
    edge_n = e1.intersection(e2)
    assert len(edge_n) == 2
  # rigid grid (nodes)
  first, second, last = nodes[0], nodes[1], nodes[-1]
  w, h = last['x'] - first['x'], last['y'] - first['y']
  step_y = second['y'] - first['y']
  rows = 1 + int(h / step_y)
  cols = int(len(nodes) / rows)
  step_x = w / (cols - 1)
  assert rows * cols == len(nodes)
  for idx, node in enumerate(nodes):
    assert node['y'] == first['y'] + step_y * (idx % rows)
    assert node['x'] == first['x'] + step_x * (idx // rows)
  # rigid grid (elements)
  for x in range(0, cols-1):
    for y in range(0, rows-1):
      i = x*(rows-1)+y
      e1 = elements[i*2]
      e2 = elements[i*2+1]
      node_id = x*rows+y
      assert sorted(e1['nodes']) == sorted([node_id, node_id+1, node_id+1+rows])
      assert sorted(e2['nodes']) == sorted([node_id, node_id+rows, node_id+1+rows])

def lookup_mesh_element(grid, gcoord, mesh):
  """"
    retrieve elements from mesh according to corresponding
    coordinates in the equivalent grid.
    @param grid
            a 2d grid
    @param gcoord
            [x,y] coordinate of the grid
    @param mesh
            the well-defined mesh
    @return a list of element IDs from the mesh
  """
  x, y = gcoord
  w, h = grid.shape
  i = x * h + y
  elements = mesh['elements']
  return [elements[i*2]['id'], elements[i*2+1]['id']]

def scale_to_grid(mesh):
  """
    Scale the mesh down to a structural grid.
    Every two consecutive elements (i.e. triangles) of the mesh
    are represented with a single cell of the grid.

    @param mesh
            a well-defined mesh object
    @return numpy 2d array representing the mesh as a grid structure
  """
  elements = mesh['elements']
  nodes = mesh['nodes']
  values = mesh['values']
  first, second, last = nodes[0], nodes[1], nodes[-1]
  w, h = last['x'] - first['x'], last['y'] - first['y']
  step_y = second['y'] - first['y']
  rows = 1 + int(h / step_y)
  cols = int(len(nodes) / rows)
  grid = np.zeros((cols-1, rows-1))
  for x in range(0, cols-1):
    grid_y = np.zeros((rows-1,))
    for y in range(0, rows-1):
      i = x*(rows-1)+y
      grid_y[y] = (values[i*2]['value'] + values[i*2+1]['value']) / 2.0
    grid[x] = grid_y
  return grid