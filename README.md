# Vision - Convex Hull and Sentry Visibility Analyzer

A Python GUI application for placing obstacle and sentry points, computing convex hulls to create fenced areas, and analyzing sentry visibility relative to the convex hull.

## Features

- **Interactive Point Placement**: Click on the canvas to place obstacle or sentry points
- **Point Types**:
  - **Obstacles** (red): Points used to compute the convex hull (fenced area)
  - **Sentries** (blue): Points analyzed for visibility outside the convex hull
- **Convex Hull Computation**: Automatically computes the smallest convex polygon enclosing all obstacles
- **Sentry Visibility Analysis**: Uses cross-product method to determine how many sentries can view outside the convex hull
- **Point Management**:
  - Edit point coordinates via inline edit button (✎)
  - Delete individual points via inline delete button (✕)
  - Clear all points at once
- **CSV Import/Export**:
  - Save points and analysis results to timestamped CSV files
  - Load points from previously saved CSV files
- **Three-Line Status Display**: Clear, separated status information for points, fence vertices, and sentry visibility
- **Scrollable Point List**: View all points with smooth scrolling (mouse wheel supported)

## Requirements

- Python 3.x
- Standard library only (tkinter, csv, datetime, os, math)

## How to Run

```bash
python3 ui.py
```

## Usage Guide

### Placing Points

1. **Select point type**: Choose "Obstacle" or "Sentry" in the "Point type" selector
2. **Click on canvas**: Left-click anywhere on the white canvas to place a point
   - Obstacles appear as **red circles** labeled "O1", "O2", etc.
   - Sentries appear as **blue circles** labeled "S1", "S2", etc.
3. **View in list**: Each placed point appears in the scrollable list on the right

**Note**: The order of placing obstacles doesn't matter - the convex hull will automatically find the fenced area.

### Computing Convex Hull

1. **Place obstacles**: Add at least 3 obstacle points
2. **Click "Compute"**: The convex hull will be drawn as a blue polygon enclosing all obstacles
3. **View results**: The status display shows three separate lines:
   - **Points**: Total number of points placed
   - **Fence vertices**: Number of vertices in the convex hull (or special messages for 0/1/2 obstacles)
   - **Sentries viewing outside**: Count and ratio (format: X/Y where X can see outside, Y total sentries)

**Note**: 
- The convex hull is the smallest convex polygon that contains all obstacle points
- If fewer than 3 obstacles are placed, all sentries are considered to view outside
- Sentries on the boundary of the convex hull can also view outside

### Managing Points

**Edit a point**:
1. Click the **✎** (edit) button next to the point in the list
2. Enter new X and Y coordinates in the dialog
3. Click "Save" to update (or "Cancel" to discard)

**Delete a point**:
- Click the **✕** (delete) button next to the point in the list
- The point is removed immediately from canvas and list
- All remaining points are renumbered
- **Note**: Deleting an obstacle will change the fence shape

**Clear all points**:
- Click the "Clear" button at the bottom
- Confirm the action in the dialog
- All points, fence, and results are cleared

### Saving and Loading

**Save to CSV**:
1. Click "Save CSV"
2. A timestamped file is created (e.g., `clicks_20251026_212017.csv`)
3. The file contains:
   - Sentry visibility result (if convex hull was computed)
   - All points with index, type, x, y coordinates

**Load from CSV**:
1. Click "Load CSV"
2. Select a previously saved CSV file
3. All points are loaded and displayed on the canvas
4. Click "Compute" to compute the convex hull

### CSV Format

```csv
Sentries viewing outside,1/3

index,type,x,y
1,obstacle,130,81
2,obstacle,53,232
3,sentry,266,144
...
```

## Algorithms

- **Convex Hull**: Graham's scan algorithm to compute the convex hull of obstacle points
  - Finds the smallest convex polygon enclosing all obstacles
  - Uses polar angle sorting from the lowest point
  - Counter-clockwise traversal with cross-product tests
- **Point-in-Polygon Test**: Cross-product method for convex polygons
  - Determines if a point is inside, outside, or on the boundary
  - Works by checking if the point is on the left side of all edges
  - Optimized for convex hulls (counter-clockwise vertex order)

## Project Files

- `ui.py` - Main GUI application (Vision class with trace() method for convex hull computation)
- `convex_hull.py` - Graham scan algorithm for convex hull computation
- `position.py` - Cross-product method for point-in-polygon testing (optimized for convex polygons)
- `README.md` - This documentation

## Tips

- **Order doesn't matter**: Place obstacles anywhere - the convex hull algorithm will find the fenced area
- Use mouse wheel to scroll through long point lists
- Edit points to fine-tune coordinates instead of deleting and re-placing
- Load CSV files to quickly test different configurations
- The convex hull automatically clears when you add, edit, or delete points (you need to click "Compute" again)
- The convex hull will always be a convex polygon, even if you place obstacles in a non-convex pattern

## Example Workflow

1. Place 5-6 obstacle points scattered around the canvas
2. Place 2-3 sentry points (some inside, some outside the expected convex hull)
3. Click "Compute" to see the convex hull and visibility count
4. Click "Save CSV" to export the configuration
5. Later, click "Load CSV" to restore and modify the configuration

## About Convex Hulls

A **convex hull** is the smallest convex polygon that encloses all the given points. Think of it like stretching a rubber band around all the obstacle points - it will form a convex shape.

Properties:
- Always creates a **convex** polygon (no indentations)
- Uses only the outermost obstacle points as vertices
- Interior obstacles don't affect the hull shape
- Represents the minimal fenced area containing all obstacles
