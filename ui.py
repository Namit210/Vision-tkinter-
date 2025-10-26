import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import datetime
import os
from position import point_position
from convex_hull import convex_hull



class Vision:
	def __init__(self, root):
		self.root = root
		self.root.title("Vision")
		self.points = []

		# Configure grid
		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(0, weight=1)

		# Canvas where user will click
		self.canvas = tk.Canvas(self.root, bg="white")
		self.canvas.grid(row=0, column=0, sticky="nsew")
		self.canvas.bind("<Button-1>", self.on_click)

		# Right-side frame for controls and list
		right_frame = ttk.Frame(self.root, width=380)
		right_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
		right_frame.grid_propagate(False)

		# Point type selector (Obstacle / Sentry)
		type_frame = ttk.LabelFrame(right_frame, text="Point type")
		type_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
		self.point_type_var = tk.StringVar(value="obstacle")
		ob_rb = ttk.Radiobutton(type_frame, text="Obstacle", value="obstacle", variable=self.point_type_var)
		ob_rb.grid(row=0, column=0, padx=4, pady=4, sticky="w")
		s_rb = ttk.Radiobutton(type_frame, text="Sentry", value="sentry", variable=self.point_type_var)
		s_rb.grid(row=0, column=1, padx=4, pady=4, sticky="w")

		# Points list with scrollbar (using canvas for custom layout with delete buttons)
		list_container = ttk.Frame(right_frame)
		list_container.grid(row=1, column=0, columnspan=2, sticky="nsew")
		
		self.points_canvas = tk.Canvas(list_container, bg="white", highlightthickness=1, highlightbackground="gray")
		self.points_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		points_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.points_canvas.yview)
		points_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.points_canvas.config(yscrollcommand=points_scrollbar.set)
		
		# Frame inside canvas to hold point entries
		self.points_frame = tk.Frame(self.points_canvas, bg="white")
		self.canvas_window = self.points_canvas.create_window((0, 0), window=self.points_frame, anchor="nw")
		
		# Update scroll region when frame size changes
		self.points_frame.bind("<Configure>", lambda e: self.points_canvas.configure(scrollregion=self.points_canvas.bbox("all")))
		
		def on_canvas_configure(event):
			self.points_canvas.itemconfig(self.canvas_window, width=event.width)
		self.points_canvas.bind("<Configure>", on_canvas_configure)
		
		def on_mousewheel(event):
			self.points_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
		self.points_canvas.bind_all("<MouseWheel>", on_mousewheel)
		
		# Store references to point entry widgets for updates
		self.point_widgets = []

		# Buttons
		btn_frame = ttk.Frame(right_frame)
		btn_frame.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky="ew")
		btn_frame.columnconfigure((0, 1, 2, 3), weight=1)

		load_btn = ttk.Button(btn_frame, text="Load CSV", command=self.load_csv)
		load_btn.grid(row=0, column=0, padx=2, sticky="ew")

		save_btn = ttk.Button(btn_frame, text="Save CSV", command=self.save_csv)
		save_btn.grid(row=0, column=1, padx=2, sticky="ew")

		hull_btn = ttk.Button(btn_frame, text="Compute", command=self.trace)
		hull_btn.grid(row=0, column=2, padx=2, sticky="ew")

		clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
		clear_btn.grid(row=0, column=3, padx=2, sticky="ew")
		
		# Status labels (3 separate lines)
		status_frame = ttk.Frame(right_frame)
		status_frame.grid(row=3, column=0, columnspan=2, pady=(8, 0), sticky="ew")
		
		self.status_points = ttk.Label(status_frame, text="Points: 0")
		self.status_points.pack(anchor="w", pady=1)
		
		self.status_fence = ttk.Label(status_frame, text="Fence vertices: -")
		self.status_fence.pack(anchor="w", pady=1)
		
		self.status_sentries = ttk.Label(status_frame, text="Sentries viewing outside: -")
		self.status_sentries.pack(anchor="w", pady=1)

		# Make the list container (row 1) expand to fill vertical space
		right_frame.rowconfigure(1, weight=1)
		# Make sure type_frame (row 0) doesn't expand
		right_frame.rowconfigure(0, weight=0)

		# IDs of canvas items that represent the hull (so we can clear them)
		self.hull_ids = []
		
		# Store the last computed sentry visibility count
		self.sentries_viewing_outside = None

	def update_status(self, fence_vertices=None, sentries_viewing=None):
		"""Update the status labels with current information."""
		# Always update points count
		self.status_points.config(text=f"Points: {len(self.points)}")
		
		# Update fence vertices
		if fence_vertices is None:
			self.status_fence.config(text="Fence vertices: -")
		else:
			self.status_fence.config(text=f"Fence vertices: {fence_vertices}")
		
		# Update sentries viewing outside
		if sentries_viewing is None:
			self.status_sentries.config(text="Sentries viewing outside: -")
		else:
			viewing, total = sentries_viewing
			self.status_sentries.config(text=f"Sentries viewing outside: {viewing}/{total}")

	def on_click(self, event):
		x, y = int(event.x), int(event.y)
		ptype = self.point_type_var.get()  # 'obstacle' or 'sentry'
		# store point as (type, x, y)
		self.points.append((ptype, x, y))

		# Draw a slightly larger marker on the canvas with distinct colors per type
		r = 6  # increased point size
		color = "red" if ptype == "obstacle" else "blue"
		self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
		idx = len(self.points)
		# label the point with its index and type
		label = "O" if ptype == "obstacle" else "S"
		self.canvas.create_text(x + 8, y - 8, text=f"{label}{idx}", anchor="nw", font=("Arial", 9), fill=color)

		# Add to points list with delete button
		self.add_point_to_list(idx, ptype, x, y)
		self.update_status()

		# If there's an existing hull drawn, remove it (points changed)
		if self.hull_ids:
			for _id in self.hull_ids:
				self.canvas.delete(_id)
			self.hull_ids = []
			self.sentries_viewing_outside = None  # reset sentry count when points change
			# Update status to reflect hull removed
			self.update_status()

	def add_point_to_list(self, idx, ptype, x, y):
		"""Add a point entry with inline edit and delete buttons to the points list."""
		label = "O" if ptype == "obstacle" else "S"
		color = "red" if ptype == "obstacle" else "blue"
		
		# Create frame for this point entry
		entry_frame = tk.Frame(self.points_frame, bg="white")
		entry_frame.pack(fill=tk.X, padx=2, pady=1)
		
		# Label showing point info
		point_label = tk.Label(entry_frame, text=f"{idx} [{label}]: ({x}, {y})", 
		                       fg=color, anchor="w", font=("Arial", 9), bg="white")
		point_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
		
		# Edit button for this point
		edit_btn = ttk.Button(entry_frame, text="✎", width=3, 
		                      command=lambda i=idx-1: self.edit_point_by_index(i))
		edit_btn.pack(side=tk.RIGHT, padx=1)
		
		# Delete button for this point
		del_btn = ttk.Button(entry_frame, text="✕", width=3, 
		                     command=lambda i=idx-1: self.delete_point_by_index(i))
		del_btn.pack(side=tk.RIGHT)
		
		self.point_widgets.append(entry_frame)

	def refresh_points_list(self):
		"""Clear and rebuild the entire points list display."""
		# Clear existing widgets
		for widget in self.point_widgets:
			widget.destroy()
		self.point_widgets.clear()
		
		# Rebuild from current points data
		for i, (ptype, x, y) in enumerate(self.points, start=1):
			self.add_point_to_list(i, ptype, x, y)

	def delete_point_by_index(self, idx):
		"""Delete a point by its 0-based index in the points list."""
		if 0 <= idx < len(self.points):
			# Remove from data
			del self.points[idx]
			
			# Clear hull if it exists
			if self.hull_ids:
				for _id in self.hull_ids:
					self.canvas.delete(_id)
				self.hull_ids = []
				self.sentries_viewing_outside = None
			
			# Redraw all points on canvas
			self.canvas.delete("all")
			for i, (ptype, x, y) in enumerate(self.points, start=1):
				r = 6
				color = "red" if ptype == "obstacle" else "blue"
				self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
				label = "O" if ptype == "obstacle" else "S"
				self.canvas.create_text(x + 8, y - 8, text=f"{label}{i}", anchor="nw", font=("Arial", 9), fill=color)
			
			# Refresh the points list
			self.refresh_points_list()
			
			# Update status
			self.update_status()

	def edit_point_by_index(self, idx):
		"""Edit a point's coordinates via a dialog."""
		if 0 <= idx < len(self.points):
			ptype, old_x, old_y = self.points[idx]
			
			# Create a simple dialog to get new coordinates
			dialog = tk.Toplevel(self.root)
			dialog.title("Edit Point")
			dialog.geometry("250x120")
			dialog.transient(self.root)
			dialog.grab_set()
			
			# X coordinate
			ttk.Label(dialog, text="X coordinate:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
			x_var = tk.StringVar(value=str(old_x))
			x_entry = ttk.Entry(dialog, textvariable=x_var, width=15)
			x_entry.grid(row=0, column=1, padx=10, pady=5)
			
			# Y coordinate
			ttk.Label(dialog, text="Y coordinate:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
			y_var = tk.StringVar(value=str(old_y))
			y_entry = ttk.Entry(dialog, textvariable=y_var, width=15)
			y_entry.grid(row=1, column=1, padx=10, pady=5)
			
			def save_edit():
				try:
					new_x = int(x_var.get())
					new_y = int(y_var.get())
					
					# Update the point
					self.points[idx] = (ptype, new_x, new_y)
					
					# Clear hull if it exists
					if self.hull_ids:
						for _id in self.hull_ids:
							self.canvas.delete(_id)
						self.hull_ids = []
						self.sentries_viewing_outside = None
					
					# Redraw all points on canvas
					self.canvas.delete("all")
					for i, (pt, x, y) in enumerate(self.points, start=1):
						r = 6
						color = "red" if pt == "obstacle" else "blue"
						self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
						label = "O" if pt == "obstacle" else "S"
						self.canvas.create_text(x + 8, y - 8, text=f"{label}{i}", anchor="nw", font=("Arial", 9), fill=color)
					
					# Refresh the points list
					self.refresh_points_list()
					
					dialog.destroy()
				except ValueError:
					messagebox.showerror("Invalid input", "Please enter valid integer coordinates.", parent=dialog)
			
			# Buttons
			btn_frame = ttk.Frame(dialog)
			btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
			
			ttk.Button(btn_frame, text="Save", command=save_edit).pack(side=tk.LEFT, padx=5)
			ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
			
			x_entry.focus()
			x_entry.select_range(0, tk.END)


	def trace(self):
		if self.hull_ids:
			for _id in self.hull_ids:
				self.canvas.delete(_id)
			self.hull_ids = []

		# Gather obstacle points in insertion order and sentry points
		obstacles = [(x, y) for (t, x, y) in self.points if t == "obstacle"]
		sentries = [(x, y) for (t, x, y) in self.points if t == "sentry"]
		
		# Handle cases with less than 3 obstacles
		if len(obstacles) == 0:
			sentries_outside = len(sentries)
			self.sentries_viewing_outside = (sentries_outside, len(sentries))
			self.update_status(fence_vertices=0, sentries_viewing=(sentries_outside, len(sentries)))
			return
		
		if len(obstacles) == 1:
			# Single obstacle - just mark it, all sentries can view outside
			x, y = obstacles[0]
			r = 6
			cid = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="", outline="blue", width=2)
			tid = self.canvas.create_text(x + 6, y - 6, text="1", anchor="nw", font=("Arial", 9), fill="blue")
			self.hull_ids.extend([cid, tid])
			
			sentries_outside = len(sentries)
			self.sentries_viewing_outside = (sentries_outside, len(sentries))
			self.update_status(fence_vertices=1, sentries_viewing=(sentries_outside, len(sentries)))
			return
		
		if len(obstacles) == 2:
			# Two obstacles 
			x1, y1 = obstacles[0]
			x2, y2 = obstacles[1]
			
			# Draw line
			line_id = self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
			self.hull_ids.append(line_id)
			
			# Draw markers for both endpoints
			r = 6
			for i, (x, y) in enumerate(obstacles, start=1):
				cid = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="", outline="blue", width=2)
				tid = self.canvas.create_text(x + 6, y - 6, text=str(i), anchor="nw", font=("Arial", 9), fill="blue")
				self.hull_ids.extend([cid, tid])
			
			sentries_outside = len(sentries)
			self.sentries_viewing_outside = (sentries_outside, len(sentries))
			self.update_status(fence_vertices=2, sentries_viewing=(sentries_outside, len(sentries)))
			return

		# 3 or more obstacles - compute convex hull
		hull = convex_hull(obstacles)
		
		# Close the polygon for drawing and testing
		polygon = hull + [hull[0]]

		# Draw the convex hull (outline only)
		flat = []
		for (x, y) in polygon:
			flat.extend((x, y))
		poly_id = self.canvas.create_polygon(*flat, outline="blue", fill="", width=2)
		self.hull_ids.append(poly_id)

		# Draw markers for hull vertices
		r = 6
		for i, (x, y) in enumerate(hull, start=1):
			cid = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="", outline="blue", width=2)
			tid = self.canvas.create_text(x + 6, y - 6, text=str(i), anchor="nw", font=("Arial", 9), fill="blue")
			self.hull_ids.extend([cid, tid])

		sentries_outside = 0
		for sentry in sentries:
			pos = point_position(polygon, sentry)
			if pos <= 0:  # outside (-1) or on boundary (0)
				sentries_outside += 1

		# Store the result for CSV export
		self.sentries_viewing_outside = (sentries_outside, len(sentries))

		# Update status
		self.update_status(fence_vertices=len(hull), sentries_viewing=(sentries_outside, len(sentries)))

	def load_csv(self):
		"""Load points from a CSV file."""
		filename = filedialog.askopenfilename(
			title="Select CSV file to load",
			filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
			initialdir=os.getcwd()
		)
		
		if not filename:
			return  # User cancelled
		
		try:
			with open(filename, "r", newline="") as f:
				reader = csv.reader(f)
				rows = list(reader)
			
			# Clear existing points first
			self.points.clear()
			self.canvas.delete("all")
			self.refresh_points_list()
			if self.hull_ids:
				for _id in self.hull_ids:
					self.canvas.delete(_id)
				self.hull_ids = []
			self.sentries_viewing_outside = None
			
			# Parse rows
			loaded_count = 0
			for row in rows:
				if len(row) < 4:
					continue  # Skip empty rows or sentry result rows
				
				# Check if this is the header row
				if row[0].lower() == "index":
					continue
				
				try:
					# Parse: index, type, x, y
					ptype = row[1].strip().lower()
					x = int(row[2])
					y = int(row[3])
					
					# Validate type
					if ptype not in ["obstacle", "sentry"]:
						continue
					
					# Add the point
					self.points.append((ptype, x, y))
					
					# Draw on canvas
					r = 6
					color = "red" if ptype == "obstacle" else "blue"
					self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
					label = "O" if ptype == "obstacle" else "S"
					idx = len(self.points)
					self.canvas.create_text(x + 8, y - 8, text=f"{label}{idx}", anchor="nw", font=("Arial", 9), fill=color)
					
					loaded_count += 1
				except (ValueError, IndexError):
					continue  # Skip malformed rows
			
			# Refresh the points list display
			self.refresh_points_list()
			
			# Update status
			self.update_status()
			
			if loaded_count > 0:
				messagebox.showinfo("Loaded", f"Successfully loaded {loaded_count} points from {os.path.basename(filename)}")
			else:
				messagebox.showwarning("No data", "No valid points found in the CSV file.")
		
		except Exception as e:
			messagebox.showerror("Load error", f"Failed to load CSV: {e}")

	def save_csv(self):
		if not self.points:
			messagebox.showinfo("No data", "No coordinates to save.")
			return

		# Save to a timestamped CSV in the current working directory
		fname = datetime.datetime.now().strftime("clicks_%Y%m%d_%H%M%S.csv")
		try:
			with open(fname, "w", newline="") as f:
				writer = csv.writer(f)
				
	
				obstacles = [(x, y) for (t, x, y) in self.points if t == "obstacle"]
				if self.sentries_viewing_outside is not None and len(obstacles) >= 3:
					viewing, total = self.sentries_viewing_outside
					writer.writerow(("Sentries viewing outside", f"{viewing}/{total}"))
					writer.writerow([])  # blank row separator
				
				# Write point data
				writer.writerow(("index", "type", "x", "y"))
				for i, (ptype, x, y) in enumerate(self.points, start=1):
					writer.writerow((i, ptype, x, y))
		except Exception as e:
			messagebox.showerror("Save error", f"Failed to save CSV: {e}")
			return

		messagebox.showinfo("Saved", f"Saved {len(self.points)} points to {os.path.abspath(fname)}")

	def clear_all(self):
		if not self.points:
			return
		if not messagebox.askyesno("Clear", "Clear all recorded points?"):
			return
		self.points.clear()
		self.canvas.delete("all")
		self.refresh_points_list()
		self.hull_ids = []
		self.sentries_viewing_outside = None  # reset sentry count
		self.update_status()

	def run(self):
		self.root.mainloop()


if __name__ == "__main__":
	root = tk.Tk()
	# Default window size
	root.geometry("900x600")
	app = Vision(root)
	app.run()