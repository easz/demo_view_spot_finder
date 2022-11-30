import argparse
import json
import view_spot_finder.finder

if __name__ == '__main__':
  # args
  parser = argparse.ArgumentParser()
  parser.add_argument("mesh", help="mesh file")
  parser.add_argument("N", help="number of view spots", type=int, nargs='?', default=1)
  args = parser.parse_args()

  with open(args.mesh) as f:
    # extract parameters
    mesh = json.load(f)
    N = args.N
    # call actual bacend
    result = view_spot_finder.finder.find_spot(mesh, N)

    print(json.dumps(result, indent=4))