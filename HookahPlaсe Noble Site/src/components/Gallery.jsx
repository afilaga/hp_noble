import React, { useState } from 'react';
import { motion } from 'framer-motion';

// Динамический импорт всех изображений из папки assets/gallery
const modules = import.meta.glob('../assets/gallery/*.{png,jpg,jpeg,webp,svg}', { eager: true });

// Преобразуем модули в массив путей и сортируем
const galleryImages = Object.values(modules)
    .map(mod => mod.default)
    .sort();

const Gallery = () => {
    const [currentIndex, setCurrentIndex] = useState(0);

    const nextSlide = () => {
        setCurrentIndex((prev) => (prev + 1) % galleryImages.length);
    };

    const prevSlide = () => {
        setCurrentIndex((prev) => (prev - 1 + galleryImages.length) % galleryImages.length);
    };

    return (
        <section id="gallery" className="section gallery-section">
            <div className="container">
                <h2 className="section-title center mb-4">Интерьер</h2>
                
                <div className="gallery-wrapper">
                    <button className="gallery-btn prev" onClick={prevSlide}>&larr;</button>
                    
                    <div className="gallery-viewport">
                        <motion.div 
                            className="gallery-track-slider"
                            animate={{ x: `-${currentIndex * 100}%` }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        >
                            {galleryImages.map((src, index) => (
                                <div key={index} className="gallery-slide">
                                    <img src={src} alt={`Interior ${index + 1}`} loading="lazy" />
                                </div>
                            ))}
                        </motion.div>
                    </div>

                    <button className="gallery-btn next" onClick={nextSlide}>&rarr;</button>
                </div>
                
                <div className="gallery-dots">
                    {galleryImages.map((_, index) => (
                        <button 
                            key={index} 
                            className={`dot ${index === currentIndex ? 'active' : ''}`}
                            onClick={() => setCurrentIndex(index)}
                        />
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Gallery;
