import sys
import json
import math
import os
import shutil
import subprocess

try:
    import bpy
except ImportError:
    bpy = None


def create_material(name, color, roughness=0.25, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


def detect_theme(topic_str: str) -> str:
    t = topic_str.lower()
    if any(w in t for w in ["star", "moon", "night", "sky", "twinkle", "space", "planet"]):
        return "star"
    if any(w in t for w in ["bus", "car", "drive", "road", "wheel", "traffic", "truck"]):
        return "bus"
    if any(w in t for w in ["cow", "duck", "farm", "sheep", "pig", "macdonald", "animal", "barn"]):
        return "farm"
    if any(w in t for w in ["fruit", "apple", "banana", "berry", "vegetable", "food", "yummy"]):
        return "fruit"
    if any(w in t for w in ["train", "rail", "choo", "engine", "track", "steam", "chugga"]):
        return "train"
    return "general_preschool"


def add_cartoon_eyes(parent_obj, loc_center, eye_size=0.18, separation=0.45):
    mat_white = create_material("EyeWhite", (0.98, 0.98, 0.98, 1.0), roughness=0.15)
    mat_black = create_material("EyeBlack", (0.05, 0.05, 0.05, 1.0), roughness=0.1)

    cx, cy, cz = loc_center
    for sign in [1, -1]:
        ey = cy + (sign * separation / 2)
        # Sclera
        bpy.ops.mesh.primitive_uv_sphere_add(radius=eye_size, location=(cx, ey, cz))
        sclera = bpy.context.active_object
        sclera.data.materials.append(mat_white)
        sclera.parent = parent_obj

        # Pupil
        bpy.ops.mesh.primitive_uv_sphere_add(radius=eye_size * 0.52, location=(cx + (eye_size * 0.7), ey, cz))
        pupil = bpy.context.active_object
        pupil.data.materials.append(mat_black)
        pupil.parent = parent_obj

        # Specular Highlight sparkle
        bpy.ops.mesh.primitive_uv_sphere_add(radius=eye_size * 0.22, location=(cx + (eye_size * 0.92), ey + 0.03, cz + 0.04))
        sparkle = bpy.context.active_object
        sparkle.data.materials.append(mat_white)
        sparkle.parent = parent_obj


def add_smiling_mouth(parent_obj, loc, radius=0.22):
    mat_black = create_material("MouthBlack", (0.05, 0.05, 0.05, 1.0), roughness=0.2)
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.035, location=loc)
    smile = bpy.context.active_object
    smile.rotation_euler = (math.radians(90), 0, math.radians(90))
    smile.parent = parent_obj
    smile.data.materials.append(mat_black)


def build_scene(data):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    duration = float(data.get("duration", 5.0))
    fps = int(data.get("fps", 24))
    total_frames = max(24, int(duration * fps))

    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = total_frames

    res_x = int(data.get("res_x", 1280))
    res_y = int(data.get("res_y", 720))
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100

    output_path = data.get("output_path", "/tmp/scene.mp4")
    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)
    scene_number = int(data.get("scene_number", 1))
    frames_dir = os.path.join(out_dir, f"frames_scene_{scene_number}")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    scene.render.filepath = os.path.join(frames_dir, "frame_")
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 95

    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "BLENDER_WORKBENCH"

    topic = data.get("topic", "") or data.get("environment", "") or "preschool"
    theme = data.get("theme") or detect_theme(topic)

    # Palette
    mat_grass = create_material("GrassMat", (0.24, 0.78, 0.22, 1.0), roughness=0.55)
    mat_hill = create_material("HillMat", (0.32, 0.72, 0.28, 1.0), roughness=0.6)
    mat_yellow = create_material("BrightYellow", (1.0, 0.85, 0.08, 1.0), roughness=0.18, metallic=0.1)
    mat_blue = create_material("CandyBlue", (0.08, 0.45, 0.98, 1.0), roughness=0.15)
    mat_red = create_material("CandyRed", (0.95, 0.12, 0.15, 1.0), roughness=0.18)
    mat_white = create_material("FluffyWhite", (0.98, 0.98, 0.98, 1.0), roughness=0.25)
    mat_black = create_material("TireBlack", (0.08, 0.08, 0.08, 1.0), roughness=0.4)
    mat_pink = create_material("CheekPink", (1.0, 0.58, 0.70, 1.0), roughness=0.3)
    mat_gold = create_material("SparkleGold", (1.0, 0.90, 0.25, 1.0), roughness=0.1, metallic=0.5)
    mat_orange = create_material("SunOrange", (1.0, 0.45, 0.05, 1.0), roughness=0.2)

    # World Lighting
    world = bpy.data.worlds.new("SkyWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")

    if theme == "star":
        # Night Sky
        if bg_node:
            bg_node.inputs["Color"].default_value = (0.04, 0.06, 0.18, 1.0)
            bg_node.inputs["Strength"].default_value = 0.8
        bpy.ops.object.light_add(type="POINT", location=(4.0, -6.0, 8.0))
        key = bpy.context.active_object
        key.data.energy = 90.0
        key.data.color = (0.9, 0.95, 1.0)
    else:
        # Bright Sunny Day
        if bg_node:
            bg_node.inputs["Color"].default_value = (0.52, 0.80, 1.0, 1.0)
            bg_node.inputs["Strength"].default_value = 1.1
        bpy.ops.object.light_add(type="SUN", location=(6.0, -8.0, 14.0))
        sun = bpy.context.active_object
        sun.data.energy = 4.2
        sun.data.color = (1.0, 0.95, 0.85)
        sun.rotation_euler = (math.radians(48), math.radians(18), math.radians(35))

    # Rim Light
    bpy.ops.object.light_add(type="POINT", location=(-5.0, 7.0, 6.0))
    rim = bpy.context.active_object
    rim.data.energy = 60.0
    rim.data.color = (0.8, 0.95, 1.0)

    # Fill Light
    bpy.ops.object.light_add(type="POINT", location=(0.0, -5.0, 4.0))
    fill = bpy.context.active_object
    fill.data.energy = 35.0
    fill.data.color = (1.0, 0.98, 0.92)

    # ==========================================
    # THEME 1: TWINKLE STAR & NIGHT SKY
    # ==========================================
    if theme == "star":
        # Crescent Moon
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.8, location=(-6.0, 14.0, 7.5))
        moon = bpy.context.active_object
        moon.data.materials.append(mat_yellow)
        # Moon eyes & smile
        add_cartoon_eyes(moon, (-4.8, 12.5, 7.8), eye_size=0.15, separation=0.35)

        # Hero Star
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 1.5))
        star_root = bpy.context.active_object
        star_root.name = "TwinkleStar"

        # Star Center Body
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
        star_body = bpy.context.active_object
        star_body.scale = (0.6, 1.2, 1.2)
        star_body.data.materials.append(mat_gold)
        star_body.parent = star_root

        # 5 Star Points (Cones)
        for p_idx in range(5):
            angle = p_idx * (2 * math.pi / 5) + (math.pi / 2)
            px = 0
            py = math.cos(angle) * 1.3
            pz = math.sin(angle) * 1.3
            bpy.ops.mesh.primitive_cone_add(radius1=0.45, depth=1.1, location=(px, py, pz))
            point = bpy.context.active_object
            point.rotation_euler = (0, 0, angle - (math.pi / 2))
            point.data.materials.append(mat_yellow)
            point.parent = star_root

        add_cartoon_eyes(star_root, (0.55, 0, 0.15), eye_size=0.18, separation=0.42)
        add_smiling_mouth(star_root, (0.60, 0, -0.22), radius=0.20)

        # Star Twinkling and floating animation
        for f in range(1, total_frames + 1, 6):
            bob = 1.5 + (0.18 if (f // 6) % 2 == 0 else -0.18)
            star_root.location.z = bob
            star_root.keyframe_insert(data_path="location", frame=f)

        star_root.keyframe_insert(data_path="rotation_euler", frame=1)
        star_root.rotation_euler.z += math.radians(180)
        star_root.keyframe_insert(data_path="rotation_euler", frame=total_frames)

        # Little background stars
        for sx, sy, sz in [(-4, 8, 4), (5, 9, 6), (7, 6, 3), (-6, 5, 2), (2, 10, 8)]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(sx, sy, sz))
            s = bpy.context.active_object
            s.data.materials.append(mat_white)

    # ==========================================
    # THEME 2: WHEELS ON THE BUS
    # ==========================================
    elif theme == "bus":
        # Rolling Road
        bpy.ops.mesh.primitive_plane_add(size=70, location=(0, 0, -0.05))
        ground = bpy.context.active_object
        ground.data.materials.append(mat_grass)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.02))
        road = bpy.context.active_object
        road.scale = (50.0, 3.8, 0.04)
        road.data.materials.append(mat_black)

        # Road Dashed White Lines
        for rx in range(-24, 25, 4):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, 0, 0.05))
            stripe = bpy.context.active_object
            stripe.scale = (1.8, 0.18, 0.03)
            stripe.data.materials.append(mat_white)

        # Hero Character: Buster the Yellow School Bus
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-4.0, 0, 1.2))
        bus_root = bpy.context.active_object
        bus_root.name = "BusterTheBus"

        # Main Bus Body
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.45))
        body = bpy.context.active_object
        body.scale = (3.4, 1.6, 1.5)
        body.data.materials.append(mat_yellow)
        body.parent = bus_root

        # Front Windshield with Eyes
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.72, 0, 0.65))
        windshield = bpy.context.active_object
        windshield.scale = (0.05, 1.35, 0.65)
        windshield.data.materials.append(mat_blue)
        windshield.parent = bus_root
        add_cartoon_eyes(bus_root, (1.80, 0, 0.65), eye_size=0.18, separation=0.6)
        add_smiling_mouth(bus_root, (1.75, 0, 0.05), radius=0.28)

        # Bus Wheels
        for wx, wy in [(1.1, 0.85), (-1.1, 0.85), (1.1, -0.85), (-1.1, -0.85)]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.22, location=(wx, wy, -0.4))
            tire = bpy.context.active_object
            tire.rotation_euler = (math.radians(90), 0, 0)
            tire.data.materials.append(mat_black)
            tire.parent = bus_root

            # Rotate wheels
            tire.keyframe_insert(data_path="rotation_euler", frame=1)
            tire.rotation_euler.y += math.radians(360 * (duration * 2.5))
            tire.keyframe_insert(data_path="rotation_euler", frame=total_frames)

        # Bus Driving & Bouncy Suspension
        bus_root.keyframe_insert(data_path="location", frame=1)
        bus_root.location.x += 8.5
        bus_root.keyframe_insert(data_path="location", frame=total_frames)

        for f in range(1, total_frames + 1, 6):
            bob = 1.2 + (0.06 if (f // 6) % 2 == 0 else -0.06)
            bus_root.location.z = bob
            bus_root.keyframe_insert(data_path="location", frame=f)

    # ==========================================
    # THEME 3: OLD MACDONALD / FARM ANIMALS
    # ==========================================
    elif theme == "farm":
        bpy.ops.mesh.primitive_plane_add(size=70, location=(0, 0, -0.05))
        ground = bpy.context.active_object
        ground.data.materials.append(mat_grass)

        # Red Barn in Background
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-6.0, 10.0, 2.2))
        barn = bpy.context.active_object
        barn.scale = (5.0, 3.5, 3.5)
        barn.data.materials.append(mat_red)

        bpy.ops.mesh.primitive_cone_add(radius1=3.2, depth=2.0, location=(-6.0, 10.0, 4.8))
        roof = bpy.context.active_object
        roof.rotation_euler = (0, 0, math.radians(45))
        roof.data.materials.append(mat_white)

        # Hero Character: Daisy the Happy Cow
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-0.5, 0, 0))
        cow_root = bpy.context.active_object
        cow_root.name = "DaisyCow"

        # Cow Body
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1.2))
        cow_body = bpy.context.active_object
        cow_body.scale = (1.2, 0.95, 1.0)
        cow_body.data.materials.append(mat_white)
        cow_body.parent = cow_root

        # Cow Head
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.68, location=(1.0, 0, 1.85))
        head = bpy.context.active_object
        head.data.materials.append(mat_white)
        head.parent = cow_root

        # Snout
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(1.55, 0, 1.7))
        snout = bpy.context.active_object
        snout.scale = (0.7, 1.1, 0.7)
        snout.data.materials.append(mat_pink)
        snout.parent = cow_root

        add_cartoon_eyes(cow_root, (1.45, 0, 2.05), eye_size=0.14, separation=0.36)
        add_smiling_mouth(cow_root, (1.75, 0, 1.62), radius=0.18)

        # Cow dancing & bouncing
        for f in range(1, total_frames + 1, 8):
            bounce_z = 0.18 if (f // 8) % 2 == 0 else 0.0
            cow_root.location.z = bounce_z
            cow_root.keyframe_insert(data_path="location", frame=f)

            rot_y = math.radians(6 if (f // 8) % 2 == 0 else -6)
            cow_root.rotation_euler.y = rot_y
            cow_root.keyframe_insert(data_path="rotation_euler", frame=f)

    # ==========================================
    # THEME 4: FRUITS & PHONICS DANCE
    # ==========================================
    elif theme == "fruit":
        bpy.ops.mesh.primitive_plane_add(size=70, location=(0, 0, -0.05))
        ground = bpy.context.active_object
        ground.data.materials.append(mat_grass)

        # Hero Character: Happy Apple
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-1.2, 0, 0))
        apple_root = bpy.context.active_object
        apple_root.name = "HappyApple"

        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(0, 0, 1.3))
        apple = bpy.context.active_object
        apple.scale = (1.05, 1.15, 1.0)
        apple.data.materials.append(mat_red)
        apple.parent = apple_root

        # Green Stem & Leaf Hat
        mat_leaf = create_material("LeafGreen", (0.1, 0.8, 0.1, 1.0), roughness=0.3)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.5, location=(0, 0, 2.45))
        stem = bpy.context.active_object
        stem.data.materials.append(mat_leaf)
        stem.parent = apple_root

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0.25, 0, 2.5))
        leaf = bpy.context.active_object
        leaf.scale = (1.2, 0.5, 0.2)
        leaf.rotation_euler = (0, math.radians(20), math.radians(30))
        leaf.data.materials.append(mat_leaf)
        leaf.parent = apple_root

        add_cartoon_eyes(apple_root, (1.05, 0, 1.5), eye_size=0.17, separation=0.45)
        add_smiling_mouth(apple_root, (1.15, 0, 1.1), radius=0.24)

        # Companion Sunny Banana
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(1.8, 0, 0))
        banana_root = bpy.context.active_object
        banana_root.name = "HappyBanana"

        bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=2.0, location=(0, 0, 1.2))
        banana = bpy.context.active_object
        banana.rotation_euler = (0, math.radians(22), 0)
        banana.data.materials.append(mat_yellow)
        banana.parent = banana_root

        add_cartoon_eyes(banana_root, (0.55, 0, 1.55), eye_size=0.12, separation=0.3)
        add_smiling_mouth(banana_root, (0.65, 0, 1.25), radius=0.16)

        # Dance hop
        for f in range(1, total_frames + 1, 6):
            apple_root.location.z = 0.25 if (f // 6) % 2 == 0 else 0.0
            apple_root.keyframe_insert(data_path="location", frame=f)

            banana_root.location.z = 0.0 if (f // 6) % 2 == 0 else 0.25
            banana_root.keyframe_insert(data_path="location", frame=f)

    # ==========================================
    # THEME 5: DEFAULT / TRAIN ADVENTURE
    # ==========================================
    else:
        # Green meadow with train tracks
        bpy.ops.mesh.primitive_plane_add(size=70, location=(0, 0, -0.05))
        ground = bpy.context.active_object
        ground.data.materials.append(mat_grass)

        # Tracks
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.55, 0.08))
        rail_l = bpy.context.active_object
        rail_l.scale = (45.0, 0.09, 0.10)
        rail_l.data.materials.append(mat_black)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.55, 0.08))
        rail_r = bpy.context.active_object
        rail_r.scale = (45.0, 0.09, 0.10)
        rail_r.data.materials.append(mat_black)

        # Hero: Toto The Train
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-4.5, 0, 0.7))
        train_root = bpy.context.active_object
        train_root.name = "TotoTheTrain"

        # Boiler
        bpy.ops.mesh.primitive_cylinder_add(radius=0.60, depth=2.0, location=(0.4, 0, 0.25))
        boiler = bpy.context.active_object
        boiler.rotation_euler = (0, math.radians(90), 0)
        boiler.parent = train_root
        boiler.data.materials.append(mat_blue)

        # Cabin
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.9, 0, 0.55))
        cabin = bpy.context.active_object
        cabin.scale = (1.0, 1.15, 1.25)
        cabin.parent = train_root
        cabin.data.materials.append(mat_blue)

        # Chimney & Rim
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.75, location=(1.1, 0, 1.0))
        chimney = bpy.context.active_object
        chimney.parent = train_root
        chimney.data.materials.append(mat_yellow)

        add_cartoon_eyes(train_root, (1.35, 0, 0.48), eye_size=0.17, separation=0.48)
        add_smiling_mouth(train_root, (1.38, 0, 0.15), radius=0.20)

        # Animated chugga chugga
        train_root.keyframe_insert(data_path="location", frame=1)
        train_root.location.x += 9.5
        train_root.keyframe_insert(data_path="location", frame=total_frames)

        for f in range(1, total_frames + 1, 6):
            bob = 0.7 + (0.05 if (f // 6) % 2 == 0 else -0.05)
            train_root.location.z = bob
            train_root.keyframe_insert(data_path="location", frame=f)

    # ==========================================
    # DYNAMIC CAMERA ANGLES BY SCENE NUMBER
    # ==========================================
    # Scene 1: Wide establishing pan
    # Scene 2: Low-angle tracking action
    # Scene 3: High 3/4 beauty view
    # Scene 4: Close-up face zoom & cheerful wave
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    scene.camera = cam

    if scene_number == 1:
        cam.location = (0.0, -9.5, 3.8)
        cam.rotation_euler = (math.radians(74), 0, 0)
        cam.keyframe_insert(data_path="location", frame=1)
        cam.location.x += 4.0
        cam.keyframe_insert(data_path="location", frame=total_frames)
    elif scene_number == 2:
        cam.location = (2.2, -5.2, 1.6)
        cam.rotation_euler = (math.radians(82), 0, math.radians(22))
        cam.keyframe_insert(data_path="location", frame=1)
        cam.location.y -= 1.0
        cam.location.x += 3.5
        cam.keyframe_insert(data_path="location", frame=total_frames)
    elif scene_number == 3:
        cam.location = (-3.5, -8.0, 5.2)
        cam.rotation_euler = (math.radians(65), 0, math.radians(-18))
        cam.keyframe_insert(data_path="location", frame=1)
        cam.location.x += 5.0
        cam.keyframe_insert(data_path="location", frame=total_frames)
    else:
        cam.location = (0.5, -4.2, 2.2)
        cam.rotation_euler = (math.radians(78), 0, math.radians(5))
        cam.keyframe_insert(data_path="location", frame=1)
        cam.location.y += 0.8
        cam.keyframe_insert(data_path="location", frame=total_frames)

    return frames_dir, total_frames, fps, output_path


def main():
    argv = sys.argv
    if "--" not in argv:
        print("Usage: blender -b --python render_scene.py -- <path_to_scene_config.json>")
        sys.exit(1)

    json_path = argv[argv.index("--") + 1]
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    frames_dir, total_frames, fps, output_path = build_scene(data)

    print(f"Rendering high-quality frames to: {frames_dir}")
    bpy.ops.render.render(animation=True)
    print("Blender Frame Render Complete!")

    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    frame_pattern = os.path.join(frames_dir, "frame_%04d.jpg")

    cmd = [
        ffmpeg_bin,
        "-y",
        "-framerate", str(fps),
        "-i", frame_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    try:
        shutil.rmtree(frames_dir)
    except Exception:
        pass

    print(f"High-quality scene written to: {output_path}")


if __name__ == "__main__":
    main()
