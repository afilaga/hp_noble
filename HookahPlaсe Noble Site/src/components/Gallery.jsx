import React, { useRef } from 'react';
import { motion, useTransform, useScroll } from 'framer-motion';

const galleryImages = [
    '/assets/gallery/Кальянная (1).jpg',
    '/assets/gallery/Кальянная (5).jpg',
    '/assets/gallery/Кальянная (10).jpg',
    '/assets/gallery/Кальянная (11).jpg',
    '/assets/gallery/Кальянная (12).jpg',
    '/assets/gallery/Кальянная (14).jpg',
    '/assets/gallery/Кальянная (16).jpg',
    '/assets/gallery/Кальянная (17).jpg',
];

const Gallery = () => {
    const targetRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: targetRef,
    });

    const x = useTransform(scrollYProgress, [0, 1], ["1%", "-95%"]);

    return (
        <section id="gallery" ref={targetRef} className="section gallery-section">
            <div className="gallery-container sticky-wrapper">
                <h2 className="section-title center mb-4">Интерьер</h2>
                <div className="overflow-hidden">
                    <motion.div style={{ x }} className="flex gap-4 gallery-track">
                        {galleryImages.map((src, index) => (
                            <div key={index} className="gallery-item">
                                <img src={src} alt={`Interior ${index + 1}`} loading="lazy" />
                            </div>
                        ))}
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default Gallery;
