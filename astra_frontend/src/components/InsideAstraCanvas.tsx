import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function InsideAstraCanvas() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050709, 0.08);

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
    camera.position.set(0, 3.5, 9);
    camera.lookAt(0, 1.5, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // --- LIGHTING ---
    const ambientLight = new THREE.AmbientLight(0x0b0e1a, 1.2);
    scene.add(ambientLight);

    const tealLight = new THREE.DirectionalLight(0x00ffd1, 3);
    tealLight.position.set(-8, 5, 2);
    scene.add(tealLight);

    const violetLight = new THREE.DirectionalLight(0x7c3aed, 3);
    violetLight.position.set(8, -2, -3);
    scene.add(violetLight);

    // --- 3D SCENE CONTENTS ---

    // 1. Perspective Grid Floor (representing wireframe grid planes receding to the horizon)
    const gridHelper = new THREE.GridHelper(40, 40, 0x00ffd1, 0x1e2740);
    gridHelper.position.y = 0;
    // Lower color opacity for background blending
    if (Array.isArray(gridHelper.material)) {
      gridHelper.material.forEach((mat) => {
        mat.transparent = true;
        mat.opacity = 0.25;
      });
    } else {
      gridHelper.material.transparent = true;
      gridHelper.material.opacity = 0.25;
    }
    scene.add(gridHelper);

    // Secondary offset grid for density and depths
    const subGridHelper = new THREE.GridHelper(40, 80, 0x7c3aed, 0x070913);
    subGridHelper.position.y = -0.05;
    if (Array.isArray(subGridHelper.material)) {
      subGridHelper.material.forEach((mat) => {
        mat.transparent = true;
        mat.opacity = 0.15;
      });
    } else {
      subGridHelper.material.transparent = true;
      subGridHelper.material.opacity = 0.15;
    }
    scene.add(subGridHelper);

    // 2. Two Large Semi-Transparent Angled Planes Floating Above the Grid (Data Layers)
    const planeGroup = new THREE.Group();

    const planeGeo = new THREE.PlaneGeometry(6, 4);

    // Layer A: Teal Tint
    const layerAMat = new THREE.MeshStandardMaterial({
      color: 0x00ffd1,
      transparent: true,
      opacity: 0.08,
      side: THREE.DoubleSide,
      wireframe: false,
      roughness: 0.1,
      metalness: 0.9,
    });
    const layerA = new THREE.Mesh(planeGeo, layerAMat);
    layerA.rotation.x = -Math.PI / 2.5;
    layerA.position.set(-2, 1.8, 0);
    planeGroup.add(layerA);

    // Wireframe edge for Layer A
    const layerAWire = new THREE.LineSegments(
      new THREE.EdgesGeometry(planeGeo),
      new THREE.LineBasicMaterial({ color: 0x00ffd1, transparent: true, opacity: 0.35 })
    );
    layerA.add(layerAWire);

    // Layer B: Violet Tint
    const layerBMat = new THREE.MeshStandardMaterial({
      color: 0x7c3aed,
      transparent: true,
      opacity: 0.08,
      side: THREE.DoubleSide,
      wireframe: false,
      roughness: 0.1,
      metalness: 0.9,
    });
    const layerB = new THREE.Mesh(planeGeo, layerBMat);
    layerB.rotation.x = -Math.PI / 2.8;
    layerB.rotation.y = Math.PI / 8;
    layerB.position.set(2, 2.4, -1);
    planeGroup.add(layerB);

    // Wireframe edge for Layer B
    const layerBWire = new THREE.LineSegments(
      new THREE.EdgesGeometry(planeGeo),
      new THREE.LineBasicMaterial({ color: 0x7c3aed, transparent: true, opacity: 0.35 })
    );
    layerB.add(layerBWire);

    scene.add(planeGroup);

    // 3. Small Glowing Particle Dots Drifting Upward (representing data points)
    const particleCount = 220;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const particleSpeeds: number[] = [];

    for (let i = 0; i < particleCount; i++) {
      // Scattered across the room
      positions[i * 3] = (Math.random() - 0.5) * 16;     // x
      positions[i * 3 + 1] = Math.random() * 8;         // y
      positions[i * 3 + 2] = (Math.random() - 0.5) * 16;   // z
      particleSpeeds.push(0.005 + Math.random() * 0.015);
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const particleMat = new THREE.PointsMaterial({
      color: 0x00ffd1,
      size: 0.05,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Create a second particle set with violet hues
    const violetParticleGeo = new THREE.BufferGeometry();
    const violetPositions = new Float32Array(particleCount * 3);
    const violetSpeeds: number[] = [];

    for (let i = 0; i < particleCount; i++) {
      violetPositions[i * 3] = (Math.random() - 0.5) * 16;
      violetPositions[i * 3 + 1] = Math.random() * 8;
      violetPositions[i * 3 + 2] = (Math.random() - 0.5) * 16;
      violetSpeeds.push(0.004 + Math.random() * 0.012);
    }

    violetParticleGeo.setAttribute('position', new THREE.BufferAttribute(violetPositions, 3));
    const violetParticleMat = new THREE.PointsMaterial({
      color: 0x7c3aed,
      size: 0.04,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
    });

    const violetParticles = new THREE.Points(violetParticleGeo, violetParticleMat);
    scene.add(violetParticles);

    // Mouse tracker
    const handleMouseMove = (event: MouseEvent) => {
      mouseRef.current = {
        x: (event.clientX / window.innerWidth) * 2 - 1,
        y: -(event.clientY / window.innerHeight) * 2 + 1,
      };
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Animation Loop
    let animationFrameId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      const elapsedTime = clock.getElapsedTime();

      // Slow drift of the layers group
      planeGroup.rotation.y = Math.sin(elapsedTime * 0.15) * 0.12;
      layerA.position.y = 1.8 + Math.sin(elapsedTime * 0.5) * 0.15;
      layerB.position.y = 2.4 + Math.cos(elapsedTime * 0.4) * 0.15;

      // Animate particles rising up
      const posArr = particles.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < particleCount; i++) {
        posArr[i * 3 + 1] += particleSpeeds[i];
        // if exceeds ceiling, wrap around
        if (posArr[i * 3 + 1] > 8) {
          posArr[i * 3 + 1] = 0;
          posArr[i * 3] = (Math.random() - 0.5) * 16;
          posArr[i * 3 + 2] = (Math.random() - 0.5) * 16;
        }
      }
      particles.geometry.attributes.position.needsUpdate = true;

      const vPosArr = violetParticles.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < particleCount; i++) {
        vPosArr[i * 3 + 1] += violetSpeeds[i];
        if (vPosArr[i * 3 + 1] > 8) {
          vPosArr[i * 3 + 1] = 0;
          vPosArr[i * 3] = (Math.random() - 0.5) * 16;
          vPosArr[i * 3 + 2] = (Math.random() - 0.5) * 16;
        }
      }
      violetParticles.geometry.attributes.position.needsUpdate = true;

      // Subtle slow camera orbital drift & mouse parallax
      const targetCamX = mouseRef.current.x * 0.8;
      const targetCamY = 3.5 + mouseRef.current.y * 0.4;
      
      camera.position.x = THREE.MathUtils.lerp(camera.position.x, targetCamX + Math.sin(elapsedTime * 0.08) * 0.8, 0.05);
      camera.position.y = THREE.MathUtils.lerp(camera.position.y, targetCamY, 0.05);
      camera.lookAt(0, 2, 0);

      renderer.render(scene, camera);
    };

    animate();

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
      id="inside_astra_3d_container" 
      ref={containerRef} 
      className="absolute inset-0 w-full h-full pointer-events-none z-0"
    />
  );
}
