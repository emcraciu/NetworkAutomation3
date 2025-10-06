from flask import Flask, render_template_string, request
import subprocess, os
from pathlib import Path

app = Flask(__name__)

SCRIPTS_DIR = Path("/tmp/pycharm_project_446/Project/Project")
PYTHON_INTERPRETER = "/home/osboxes/.virtualenvs/Project/bin/python"

DEVICES = {
    "1": ("ubuntu_configWithIperf.py", "testbed.yaml", "Ubuntu Iperf"),
    "2": ("ubuntu_docker1_config.py", "ubuntu_docker1_tesbed.yaml", "Docker1"),
    "3": ("ubuntu_docker2_config.py", "ubuntu_docker2_testbed.yaml", "Docker2"),
    "11": ("ospf.py", "testbed_ospf.yaml", "OSPF"),

    "4": ("iou1_config.py", "iou1_testbed.yaml", "IOU1"),
    "5": ("iosv_config.py", "iosv_testbed.yaml", "IOSv"),
    "6": ("csr_config.py", "csr_testbed.yaml", "CSR"),

    "12": ("bring_up_devices.py", "testbed.yaml", "Bring Up Devices"),

    "13": ("test_py_lint.py", "", "Pylint"),
}

FTD_GROUP = {
    "ftd_initial_config.py": "Initial configuration",
    "ftd_swagger.py": "Swagger",
    "try.py": "Auto Next",
    "ftd_dhcp.py": "DHCP",
    "ospf_ftd.py": "OSPF"
}

UNITTEST_GROUP = {
    "mock_connection.py": "Mock Test",
    "test_ping.py": "Ping Test",
    "unitest_device.py": "Unittest Device",
    "unitest_ospf.py": "OSPF Test",
    #"test_security.py": "Security Test",
}

HTML = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <title>Devices Configuration</title>
  <script src=\"https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.min.js\"></script>
  <style>
    body { margin:0; padding:0; background: url(\"/static/backg.png\") no-repeat center center fixed; background-size: cover; color:white; font-family: "Times New Roman", Times, serif; }
    h1 { text-align: center; margin-top: 20px; font-size: 24px; font-weight: 700; }

    .top-center {
      position: absolute; top: 10%; left: 50%; transform: translateX(-50%);
      display: flex; gap: 12px; align-items: center; justify-content: center;
    }
    .menu {
      position: absolute; top: 46%; left: 50%; transform: translate(-50%, -50%);
      width: 100%; max-width: 980px; display: flex; justify-content: space-between; padding: 0 26px;
    }

    .menu-left { display: flex; flex-direction: column; align-items: center; margin-left: -1.5cm; }
    .menu-right { display: flex; flex-direction: column; align-items: center; margin-right: -0.5cm; }

    .bottom-center {
      position: absolute; top: 15%; left: 50%; transform: translateX(-50%);
      display: flex; gap: 16px; align-items: center; justify-content: center; flex-wrap: wrap;
    }

    .button {
      background: linear-gradient(135deg, #1E2428 40%, #2f3a40 100%);
      border: none; color: white; padding: 12px 28px; text-align: center; font-size: 16px;
      margin: 10px auto; display: block; cursor: pointer; width: 240px; border-radius: 40px;
      box-shadow: 0 6px 18px -4px rgba(0,0,0,0.4), 0 1.5px 8px 0 rgba(0,0,0,0.25);
      font-family: 'Segoe UI', Arial, sans-serif; font-weight: 600; transition: box-shadow 0.2s, background 0.2s, transform 0.12s;
    }
    .button:hover { background: linear-gradient(135deg, #65bac8 60%, #ffffff 100%);
      box-shadow: 0 11px 34px -9px rgba(0,0,0,0.5), 0 3px 12px 0 rgba(0,0,0,0.35); transform: scale(1.07); }
    .button:active { transform: scale(1.13); background: linear-gradient(135deg, #1E2428 55%, #65bac8 100%); box-shadow: 0 2px 8px 0 rgba(0,0,0,0.35); }

    .dropdown-wrapper { position: relative; display: inline-block; width: 240px; }
    .dropdown-content { display: none; position: absolute; background: #2f3a40; border-radius: 10px; box-shadow: 0 6px 18px rgba(0,0,0,0.4); z-index: 1; width: 100%; }
    .dropdown-item { background: none; border: none; padding: 12px; text-align: center; font-size: 16px; width: 100%; color: white; cursor: pointer; font-weight: 600; }
    .dropdown-item:hover { background: #3c4b52; }
    .show { display: block; }
  </style>
</head>
<body>
  <h1>Devices Configuration</h1>

  <script>
  let img; let particles = []; let buffer;
  function preload() { img = loadImage("/static/img.png"); }
  function setup() {
    createCanvas(windowWidth, windowHeight); img.loadPixels(); buffer = createGraphics(img.width, img.height);
    buffer.image(img, 0, 0); buffer.loadPixels();
    for (let y = 0; y < img.height; y += 6) {
      for (let x = 0; x < img.width; x += 6) {
        let index = (x + y * img.width) * 4;
        let r = buffer.pixels[index]; let g = buffer.pixels[index+1]; let b = buffer.pixels[index+2];
        let bright = (r+g+b)/3; if (bright > 200) { let tx = x + (width - img.width) / 2; let ty = y + (height - img.height) / 3; particles.push(new Particle(tx, ty)); }
      }
    }
  }
  function draw() {
    clear();
    for (let p of particles) { p.update(); p.show(); }
    for (let i = 0; i < particles.length; i++) {
      for (let j = i+1; j < particles.length; j++) {
        let d = dist(particles[i].pos.x, particles[i].pos.y, particles[j].pos.x, particles[j].pos.y);
        if (d < 20 && random() < 0.05) { stroke(255, 80); strokeWeight(1); line(particles[i].pos.x, particles[i].pos.y, particles[j].pos.x, particles[j].pos.y); }
      }
    }
  }
  class Particle { constructor(tx, ty){ this.target=createVector(tx,ty); let side=int(random(4)); if(side===0)this.pos=createVector(random(width),-50); else if(side===1)this.pos=createVector(random(width),height+50); else if(side===2)this.pos=createVector(-50,random(height)); else this.pos=createVector(width+50,random(height)); this.vel=p5.Vector.random2D(); this.acc=createVector(); this.maxSpeed=5; this.maxForce=0.3; this.settled=false; }
    update(){ if(!this.settled){ let force=p5.Vector.sub(this.target,this.pos); let d=force.mag(); let speed=this.maxSpeed; if(d<100) speed=map(d,0,100,0,this.maxSpeed); force.setMag(speed); let steer=p5.Vector.sub(force,this.vel); steer.limit(this.maxForce); this.applyForce(steer); this.vel.add(this.acc); this.pos.add(this.vel); this.acc.mult(0); if(d<2) this.settled=true; } else { let step=p5.Vector.random2D(); step.mult(0.5); this.pos.add(step); let px=floor(this.pos.x - width/3); let py=floor(this.pos.y - height/3); if (px>=0 && py>=0 && px<img.width && py<img.height){ let index=(px+py*img.width)*4; let r=buffer.pixels[index]; let g=buffer.pixels[index+1]; let b=buffer.pixels[index+2]; let bright=(r+g+b)/3; if (bright < 200) this.pos.sub(step); } } }
    applyForce(f){ this.acc.add(f); } show(){ stroke(255); strokeWeight(2); point(this.pos.x,this.pos.y); } }

  function runScript(deviceId) {
    fetch("/run/" + deviceId, { method: "POST" })
      .then(r => r.text())
      .then(msg => {
        if (msg.includes("ran succesfully!")) {
          if (deviceId === "2") {
            const img = document.createElement("img");
              img.src = "/static/results/iperf_latest.png";
              img.style.maxWidth = "90%";
              img.style.maxHeight = "90%";

              const overlay = document.createElement("div");
              overlay.style.position = "fixed";
              overlay.style.inset = "0";
              overlay.style.background = "rgba(0,0,0,0.85)";
              overlay.style.display = "flex";
              overlay.style.alignItems = "center";
              overlay.style.justifyContent = "center";
              overlay.style.zIndex = "9999";
              overlay.onclick = () => document.body.removeChild(overlay);

              overlay.appendChild(img);
              document.body.appendChild(overlay);
          } else {
              alert(msg);
          }
        } else {
          alert(msg);
        }
      });
  }

  function runFTD(scriptName) {
    fetch("/run_group/ftd", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: "script=" + encodeURIComponent(scriptName) })
    .then(r => r.text()).then(msg => alert(msg));
  }
  function runUnit(scriptName) {
    fetch("/run_group/unittests", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: "script=" + encodeURIComponent(scriptName) })
      .then(r => r.text()).then(msg => alert(msg));
  }

  function toggleDropdown(id) {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('show');
  }
  window.onclick = function(event) {
    if (!event.target.matches('.button')) {
      let dropdowns = document.getElementsByClassName("dropdown-content");
      for (let i=0; i<dropdowns.length; i++) dropdowns[i].classList.remove("show");
    }
  }
  </script>

  <div class=\"top-center\">
    <button class=\"button\" type=\"button\" onclick=\"runScript('12')\">Bring Up Devices</button>
  </div>

  <div class=\"menu\">
    <div class=\"menu-left\">
      {% for key, (script, tb, label) in left_devices %}
        <button class=\"button\" type=\"button\" onclick=\"runScript('{{ key }}')\">{{ label }}</button>
      {% endfor %}

      <div class=\"dropdown-wrapper\">
        <button class=\"button\" type=\"button\" onclick=\"toggleDropdown('dropdown-content-ftd')\">FTD Options</button>
        <div id=\"dropdown-content-ftd\" class=\"dropdown-content\">
          {% for file, label in ftd_group.items() %}
            <button class=\"dropdown-item\" type=\"button\" onclick=\"runFTD('{{ file }}')\">{{ label }}</button>
          {% endfor %}
        </div>
      </div>
    </div>

    <div class=\"menu-right\">
      {% for key, (script, tb, label) in right_devices %}
        <button class=\"button\" type=\"button\" onclick=\"runScript('{{ key }}')\">{{ label }}</button>
      {% endfor %}
    </div>
  </div>

  <div class=\"bottom-center\">
    <div class=\"dropdown-wrapper\">
      <button class=\"button\" type=\"button\" onclick=\"toggleDropdown('dropdown-content-unittests')\">Unittests</button>
      <div id=\"dropdown-content-unittests\" class=\"dropdown-content\">
        {% for file, label in unittests.items() %}
          <button class=\"dropdown-item\" type=\"button\" onclick=\"runUnit('{{ file }}')\">{{ label }}</button>
        {% endfor %}
      </div>
    </div>
    <button class=\"button\" type=\"button\" onclick=\"runScript('13')\">Run Pylint</button>
  </div>

</body>
</html>
"""

@app.route("/")
def index():
    left_keys = ["4", "5", "6"]
    right_keys = ["1", "2", "3", "11"]

    left_devices = [(k, DEVICES[k]) for k in left_keys if k in DEVICES]
    right_devices = [(k, DEVICES[k]) for k in right_keys if k in DEVICES]

    return render_template_string(
        HTML,
        left_devices=left_devices,
        right_devices=right_devices,
        ftd_group=FTD_GROUP,
        unittests=UNITTEST_GROUP,
    )

def env_for_playwright():
    env = os.environ.copy()
    env["HOME"] = "/home/osboxes"
    env["XDG_CACHE_HOME"] = "/home/osboxes/.cache"
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(Path("/home/osboxes/.cache/ms-playwright"))
    return env

def ensure_chromium_ready():
    CACHE = Path("/home/osboxes/.cache/ms-playwright")
    if not any(CACHE.glob("chromium-*")):
        subprocess.run(
            [PYTHON_INTERPRETER, "-m", "playwright", "install", "--with-deps", "chromium"],
            check=True, env=env_for_playwright()
        )

@app.route("/run/<device_id>", methods=["POST"])
def run_device(device_id):
    if device_id not in DEVICES:
        return "Invalid Option!"

    script, testbed, label = DEVICES[device_id]
    script_path = SCRIPTS_DIR / script

    if not script_path.exists():
        return f"{script} doesn't exist!"

    env = os.environ.copy()
    if testbed:
        testbed_path = SCRIPTS_DIR / testbed
        if not testbed_path.exists():
            return f"{testbed} doesn't exist!"
        env["TESTBED"] = str(testbed_path)

    try:
        subprocess.run([PYTHON_INTERPRETER, str(script_path)], check=True, env=env, cwd=str(SCRIPTS_DIR))
        return f"{label} ran successfully!"
    except subprocess.CalledProcessError as e:
        return f"Error at {label}: {e}"

@app.route("/run_group/ftd", methods=["POST"])
def run_group_ftd():
    script = request.form["script"]
    testbed = "ftd_testbed.yaml"

    script_path = SCRIPTS_DIR / script
    testbed_path = SCRIPTS_DIR / testbed

    if not script_path.exists():
        return f"{script} doesn't exist!"
    if not testbed_path.exists():
        return f"{testbed} doesn't exist!"

    if script == "try.py":
        ensure_chromium_ready()
        try:
            subprocess.run([PYTHON_INTERPRETER, str(script_path), str(testbed_path)],
                           check=True, env=env_for_playwright(), cwd=str(SCRIPTS_DIR))
            return f"{script} ran successfully!"
        except subprocess.CalledProcessError as e:
            return f"Error at {script}: {e}"

    env = os.environ.copy(); env["TESTBED"] = str(testbed_path)
    try:
        subprocess.run([PYTHON_INTERPRETER, str(script_path)], check=True, env=env, cwd=str(SCRIPTS_DIR))
        return f"{script} ran successfully!"
    except subprocess.CalledProcessError as e:
        return f"Error at {script}: {e}"

@app.route("/run_group/unittests", methods=["POST"])
def run_group_unittests():
    script = request.form["script"]
    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        return f"{script} doesn't exist!"
    try:
        subprocess.run([PYTHON_INTERPRETER, str(script_path)], check=True, cwd=str(SCRIPTS_DIR))
        return f"{script} ran successfully!"
    except subprocess.CalledProcessError as e:
        return f"Error at {script}: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
