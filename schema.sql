-- Sistema de Gestión de Inventario
-- Dominio 3 — TechNova Solutions
-- Equipo: [nombres]

CREATE DATABASE IF NOT EXISTS inventario_db;
USE inventario_db;

-- Tabla de categorías de productos
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla principal de productos
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    categoria_id INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 0,
    precio DECIMAL(10, 2) NOT NULL,
    stock_minimo INT NOT NULL DEFAULT 5,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Tabla de movimientos de inventario (entradas y salidas)
CREATE TABLE IF NOT EXISTS movimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tipo ENUM('entrada', 'salida') NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(255),
    stock_resultante INT NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Tabla de alertas de reposición generadas automáticamente
CREATE TABLE IF NOT EXISTS alertas_reposicion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    stock_al_momento INT NOT NULL,
    stock_minimo INT NOT NULL,
    estado ENUM('pendiente', 'atendida') DEFAULT 'pendiente',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Datos de ejemplo para categorías
INSERT INTO categorias (nombre, descripcion) VALUES
('Electrónica', 'Dispositivos y accesorios electrónicos'),
('Papelería', 'Artículos de oficina y escritura'),
('Herramientas', 'Herramientas manuales y eléctricas');
