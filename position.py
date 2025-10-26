def point_position(polygon, point, eps=1e-9):
    xq, yq = point
    n = len(polygon)
    
    # Handle closed polygon (last point same as first)
    if n > 0 and polygon[0] == polygon[-1]:
        n = n - 1
    
    if n < 3:
        return -1  # Not a valid polygon
    
    # check if point is on any edge
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        
        cross = (x2 - x1)*(yq - y1) - (y2 - y1)*(xq - x1)
        
        if abs(cross) < eps:
            if (min(x1, x2) - eps <= xq <= max(x1, x2) + eps and
                min(y1, y2) - eps <= yq <= max(y1, y2) + eps):
                return 0  # On the boundary
    
    # Ray casting algorithm: count intersections with edges
    intersections = 0
    
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        
        if (y1 > yq) != (y2 > yq):

            x_intersection = x1 + (yq - y1) * (x2 - x1) / (y2 - y1)
            
            if xq < x_intersection:
                intersections += 1
    
    # Odd number of intersections means inside, even means outside
    if intersections % 2 == 1:
        return 1  # Inside
    else:
        return -1  # Outside
