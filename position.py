def point_position(polygon, point, eps=1e-9):
	xq, yq = point
	n = len(polygon)
	
	if n < 3:
		return -1  # Not a valid polygon
	
	for i in range(n):
		x1, y1 = polygon[i]
		x2, y2 = polygon[(i + 1) % n]
		
		# Cross product: (p2 - p1) × (point - p1)
		cross = (x2 - x1) * (yq - y1) - (y2 - y1) * (xq - x1)
		
		if cross < -eps:
			return -1
		elif abs(cross) < eps:

			if (min(x1, x2) - eps <= xq <= max(x1, x2) + eps and
				min(y1, y2) - eps <= yq <= max(y1, y2) + eps):
				return 0  # On the boundary
	
	return 1  # Inside
