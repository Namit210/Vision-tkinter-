# Vision - Polygon Fence and Sentry Visibility Analyzer

A Python GUI application for placing obstacle and sentry points, forming polygon fences by connecting obstacles in order, and analyzing sentry visibility relative to the fence.

## Features

- **Interactive Point Placement**: Click on the canvas to place obstacle or sentry points
- **Point Types**:
  - **Obstacles** (red): Points connected in order to form a polygon fence
  - **Sentries** (blue): Points analyzed for visibility outside the fence
- **Polygon Fence Formation**: Connects obstacle points in the order they were placed to form a fence (supports concave polygons)
- **Sentry Visibility Analysis**: Uses ray casting algorithm to determine how many sentries can view outside the polygon fence
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

**Important**: Obstacle points are connected in the order you place them to form the fence polygon.

### Computing Polygon Fence

1. **Place obstacles**: Add at least 3 obstacle points in the desired order
2. **Click "Compute"**: The polygon fence will be drawn by connecting consecutive obstacles with blue lines
3. **View results**: The status display shows three separate lines:
   - **Points**: Total number of points placed
   - **Fence vertices**: Number of obstacles forming the fence (or special messages for 0/1/2 obstacles)
   - **Sentries viewing outside**: Count and ratio (format: X/Y where X can see outside, Y total sentries)

**Note**: 
- The fence is formed by connecting obstacles in insertion order (O1→O2→O3→...→O1)
- If fewer than 3 obstacles are placed, all sentries are considered to view outside
- Sentries on the boundary of the fence can also view outside

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
   - Sentry visibility result (if fence was computed)
   - All points with index, type, x, y coordinates (in insertion order)

**Load from CSV**:
1. Click "Load CSV"
2. Select a previously saved CSV file
3. All points are loaded in the same order and displayed on the canvas
4. Click "Compute" to draw the fence

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

- **Polygon Fence**: Consecutive obstacles are connected in insertion order to form a closed polygon
- **Point-in-Polygon Test**: Ray casting algorithm (even-odd rule) to determine if a point is inside, outside, or on the boundary of a polygon
  - Works correctly for both convex and concave polygons
  - Counts ray intersections from the point to the right
  - Odd intersections = inside, even intersections = outside
  - Boundary detection via cross-product method with epsilon tolerance

## Project Files

- `ui.py` - Main GUI application (Vision class with trace() method for fence computation)
- `position.py` - Ray casting algorithm for point-in-polygon testing
- `README.md` - This documentation

## Tips

- **Order matters**: Place obstacles in the order you want them connected to form the fence
- Use mouse wheel to scroll through long point lists
- Edit points to fine-tune coordinates instead of deleting and re-placing
- Load CSV files to quickly test different configurations
- The fence automatically clears when you add, edit, or delete points (you need to click "Compute" again)
- To create a specific fence shape, plan the order of obstacle placement

## Example Workflow

1. Place 5-6 obstacle points in order around the perimeter of a shape
2. Place 2-3 sentry points (some inside, some outside the expected fence)
3. Click "Compute" to see the fence and visibility count
4. Click "Save CSV" to export the configuration
5. Later, click "Load CSV" to restore and modify the configuration

## Polygon Fence Behavior

This application creates a **polygon fence** by connecting obstacles in **insertion order**. This means:
- The fence can be **concave** (have indentations, L-shapes, star shapes, etc.)
- The order of placing obstacles determines the fence shape
- You have full control over the fence geometry
- The ray casting algorithm correctly handles all polygon types
