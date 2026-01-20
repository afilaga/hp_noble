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
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                >
                    <h2 className="section-title center mb-4">Интерьер</h2>

                    <div className="gallery-wrapper">
                        <button className="gallery-btn prev" onClick={prevSlide} aria-label="Предыдущее фото">&larr;</button>

                        <div className="gallery-viewport">
                            <motion.div
                                className="gallery-track-slider"
                                animate={{ x: `-${currentIndex * 100}%` }}
                                transition={{
                                    duration: 0.8,
                                    ease: [0.2, 1, 0.3, 1]
                                }}
                            >
                                {galleryImages.map((src, index) => (
                                    <div key={index} className="gallery-slide">
                                        <motion.img
                                            src={src}
                                            alt={`Interior ${index + 1}`}
                                            loading="lazy"
                                            initial={{ scale: 1.1 }}
                                            animate={{ scale: index === currentIndex ? 1 : 1.1 }}
                                            transition={{ duration: 1.2, ease: [0.2, 1, 0.3, 1] }}
                                        />
                                    </div>
                                ))}
                            </motion.div>
                        </div>

                        <button className="gallery-btn next" onClick={nextSlide} aria-label="Следующее фото">&rarr;</button>
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
                </motion.div>
            </div>
        </section>
    );
};

export default Gallery;
