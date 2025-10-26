import math

#Graham's Scan
def convex_hull(points):
	if len(points) < 3:
		return points
	
	# Find the point with the lowest y-coordinate (and leftmost if tie)
	start = min(points, key=lambda p: (p[1], p[0]))
	
	# Sort points by polar angle with respect to start point
	def polar_angle_key(p):
		dx = p[0] - start[0]
		dy = p[1] - start[1]
		angle = math.atan2(dy, dx)
		distance = dx * dx + dy * dy
		return (angle, distance)
	
	sorted_points = sorted(points, key=polar_angle_key)
	
	# Build the convex hull
	hull = []
	
	for p in sorted_points:
		# Remove points that make a clockwise turn
		while len(hull) > 1 and cross_product(hull[-2], hull[-1], p) <= 0:
			hull.pop()
		hull.append(p)
	
	return hull

def cross_product(o, a, b):
	return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
