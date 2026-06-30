import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function HeroSatelliteCanvas() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Create scene, camera, and renderer
    const scene = new THREE.Scene();
    
    // Transparent or very dark background
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.z = 12;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // --- LIGHTING ---
    // Ambient light for subtle visibility
    const ambientLight = new THREE.AmbientLight(0x0b0e1a, 1.5);
    scene.add(ambientLight);

    // High-contrast teal key light from front-left
    const tealLight = new THREE.DirectionalLight(0x00ffd1, 3);
    tealLight.position.set(-5, 3, 5);
    scene.add(tealLight);

    // Deep violet rim light from back-right for gorgeous dual-tone contrast
    const violetLight = new THREE.DirectionalLight(0x7c3aed, 5);
    violetLight.position.set(5, -3, -5);
    scene.add(violetLight);

    // Subtler blue fill light
    const blueLight = new THREE.DirectionalLight(0x002288, 2);
    blueLight.position.set(0, 5, -2);
    scene.add(blueLight);

    // --- MODEL DESIGN: STYLIZED LOW-POLY SATELLITE ---
    const satelliteGroup = new THREE.Group();

    // 1. Core Chassis (Octagonal Prism or Box)
    const chassisGeo = new THREE.BoxGeometry(1.6, 2.2, 1.6);
    const chassisMat = new THREE.MeshStandardMaterial({
      color: 0x111625,
      roughness: 0.1,
      metalness: 0.9,
      bumpScale: 0.05,
    });
    const chassis = new THREE.Mesh(chassisGeo, chassisMat);
    satelliteGroup.add(chassis);

    // Wireframe overlay for a modern digital aesthetic
    const chassisWireframe = new THREE.LineSegments(
      new THREE.EdgesGeometry(chassisGeo),
      new THREE.LineBasicMaterial({ color: 0x00ffd1, transparent: true, opacity: 0.4 })
    );
    chassis.add(chassisWireframe);

    // 2. Solar Panels (Left & Right Wings)
    const panelGroupL = new THREE.Group();
    const panelGroupR = new THREE.Group();

    const panelGeo = new THREE.BoxGeometry(2.8, 1.2, 0.08);
    // Dark metallic material for solar cells
    const panelMat = new THREE.MeshStandardMaterial({
      color: 0x070913,
      roughness: 0.3,
      metalness: 0.8,
    });

    const panelL = new THREE.Mesh(panelGeo, panelMat);
    panelL.position.x = -2.2;
    panelGroupL.add(panelL);

    const panelR = new THREE.Mesh(panelGeo, panelMat);
    panelR.position.x = 2.2;
    panelGroupR.add(panelR);

    // Solar panel grids (Teal wireframes overlaying the boxes)
    const panelWireGeo = new THREE.EdgesGeometry(panelGeo);
    const panelWireMat = new THREE.LineBasicMaterial({ color: 0x00ffd1, transparent: true, opacity: 0.6 });

    const panelLWire = new THREE.LineSegments(panelWireGeo, panelWireMat);
    panelLWire.position.x = -2.2;
    panelGroupL.add(panelLWire);

    const panelRWire = new THREE.LineSegments(panelWireGeo, panelWireMat);
    panelRWire.position.x = 2.2;
    panelGroupR.add(panelRWire);

    // Connectors (Stems connecting panel to chassis)
    const stemGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 8);
    stemGeo.rotateZ(Math.PI / 2);
    const stemMat = new THREE.MeshStandardMaterial({ color: 0x1e2740, metalness: 0.9 });
    
    const stemL = new THREE.Mesh(stemGeo, stemMat);
    stemL.position.x = -0.8;
    panelGroupL.add(stemL);

    const stemR = new THREE.Mesh(stemGeo, stemMat);
    stemR.position.x = 0.8;
    panelGroupR.add(stemR);

    satelliteGroup.add(panelGroupL);
    satelliteGroup.add(panelGroupR);

    // 3. Communications Dish / Antenna
    const dishGeo = new THREE.ConeGeometry(0.6, 0.5, 12, 1, true);
    dishGeo.rotateX(Math.PI);
    const dishMat = new THREE.MeshStandardMaterial({
      color: 0x1e2740,
      metalness: 0.8,
      roughness: 0.2,
      side: THREE.DoubleSide
    });
    const dish = new THREE.Mesh(dishGeo, dishMat);
    dish.position.y = 1.4;
    satelliteGroup.add(dish);

    const dishWire = new THREE.LineSegments(
      new THREE.EdgesGeometry(dishGeo),
      new THREE.LineBasicMaterial({ color: 0x00ffd1, transparent: true, opacity: 0.5 })
    );
    dishWire.position.y = 1.4;
    satelliteGroup.add(dishWire);

    // 4. Glowing Teal Radiation Shield Ring around the satellite
    const ringGeo = new THREE.TorusGeometry(3.6, 0.08, 8, 48);
    ringGeo.rotateX(Math.PI / 2.3); // Slightly angled tilt
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x00ffd1,
      transparent: true,
      opacity: 0.85,
    });
    const shieldRing = new THREE.Mesh(ringGeo, ringMat);
    satelliteGroup.add(shieldRing);

    // Glowing wireframe ring slightly larger
    const outerRingGeo = new THREE.TorusGeometry(3.62, 0.12, 3, 24);
    outerRingGeo.rotateX(Math.PI / 2.3);
    const outerRingMat = new THREE.MeshBasicMaterial({
      color: 0x7c3aed,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const outerShieldRing = new THREE.Mesh(outerRingGeo, outerRingMat);
    satelliteGroup.add(outerShieldRing);

    // 5. Shield Ring Particles
    const particleCount = 60;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const speeds = new Float32Array(particleCount);
    const angles = new Float32Array(particleCount);
    const radii = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      angles[i] = Math.random() * Math.PI * 2;
      radii[i] = 3.4 + Math.random() * 0.4; // near the ring
      speeds[i] = 0.01 + Math.random() * 0.02;

      const x = Math.cos(angles[i]) * radii[i];
      const z = Math.sin(angles[i]) * radii[i];
      const y = (Math.random() - 0.5) * 0.4; // slight vertical spreading

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x00ffd1,
      size: 0.06,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
    });
    const shieldParticles = new THREE.Points(particleGeo, particleMat);
    
    // Orbit angle offset helper
    shieldParticles.rotation.x = Math.PI / 2.3;
    satelliteGroup.add(shieldParticles);

    // Add everything to scene
    scene.add(satelliteGroup);

    // Align satellite positioning
    satelliteGroup.position.y = 0.2;
    satelliteGroup.rotation.x = 0.2;
    satelliteGroup.rotation.y = -0.4;

    // Handle Mouse Move tracking for Parallax
    const handleMouseMove = (event: MouseEvent) => {
      // Normalize between -1 and 1
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -(event.clientY / window.innerHeight) * 2 + 1;
      mouseRef.current = { x, y };
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Animation variables
    let animationFrameId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      const elapsedTime = clock.getElapsedTime();

      // Slow orbital rotate: 20s per revolution
      const rotationSpeed = (2 * Math.PI) / 20;
      satelliteGroup.rotation.y = elapsedTime * rotationSpeed;

      // Pulse the shield ring opacity
      if (shieldRing) {
        shieldRing.material.opacity = 0.5 + Math.sin(elapsedTime * 2.5) * 0.15;
      }

      // Animate shielding particles orbit rotation
      shieldParticles.rotation.z -= 0.006;

      // Mouse Parallax smooth lerping
      const targetRotX = mouseRef.current.y * 0.26; // approx 15 degrees max tilt
      const targetRotY = mouseRef.current.x * 0.26;
      
      satelliteGroup.rotation.x = THREE.MathUtils.lerp(satelliteGroup.rotation.x, 0.2 + targetRotX, 0.05);
      satelliteGroup.rotation.z = THREE.MathUtils.lerp(satelliteGroup.rotation.z, targetRotY, 0.05);

      renderer.render(scene, camera);
    };

    animate();

    // Resize handler with ResizeObserver
    const resizeObserver = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0) return;
      const entry = entries[0];
      const w = entry.contentRect.width;
      const h = entry.contentRect.height;
      
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });

    resizeObserver.observe(container);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', handleMouseMove);
      resizeObserver.disconnect();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div 
      id="hero_satellite_3d_container" 
      ref={containerRef} 
      className="w-full h-[320px] sm:h-[450px] lg:h-[500px] relative overflow-hidden cursor-grab active:cursor-grabbing"
    />
  );
}
