import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Helmet } from 'react-helmet-async';
import Loader from './components/Loader';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Gallery from './components/Gallery';
import ReservationForm from './components/ReservationForm';
import Marquee from './components/Marquee';
import Contacts from './components/Contacts';
import Footer from './components/Footer';
import AgeGate from './components/AgeGate';

function App() {
    const [loading, setLoading] = useState(true);
    const [ageVerified, setAgeVerified] = useState(false);

    const schemaData = {
        "@context": "https://schema.org",
        "@type": "HookahBar",
        "name": "HookahPlace Noble",
        "image": "https://hpnoble.ru/assets/gallery_3.jpg",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "ул. Воровского, 35А",
            "addressLocality": "Сочи",
            "addressRegion": "Краснодарский край",
            "postalCode": "354000",
            "addressCountry": "RU"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": 43.5855,
            "longitude": 39.7231
        },
        "url": "https://hpnoble.ru",
        "telephone": "+79996556622",
        "priceRange": "$$$",
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday"
                ],
                "opens": "12:00",
                "closes": "02:00"
            }
        ]
    };

    return (
        <div className="app-container">
            <Helmet>
                <title>HookahPlace Noble — Лучшая кальянная в Сочи (Центр) | Паровые коктейли</title>
                <meta name="description" content="Премиальный лаунж-бар в центре Сочи (Воровского 35а). Авторские паровые коктейли, элитные чаи и уникальная атмосфера Noble. Бронь столов: +7 (999) 655-66-22." />
                <meta name="keywords" content="кальянная сочи, hookahplace noble, хуках плейс нобл, лаунж бар сочи, куда сходить в сочи, паровые коктейли, центр сочи" />
                <link rel="canonical" href="https://hpnoble.ru" />

                {/* Open Graph / Facebook */}
                <meta property="og:type" content="business.business" />
                <meta property="og:url" content="https://hpnoble.ru/" />
                <meta property="og:title" content="HookahPlace Noble — Лучшая кальянная в Сочи" />
                <meta property="og:description" content="Премиальный лаунж в центре Сочи. Атмосфера, стиль и лучшие мастера города." />
                <meta property="og:image" content="https://hpnoble.ru/og-image.jpg" />
                <meta property="og:locale" content="ru_RU" />

                {/* Structured Data */}
                <script type="application/ld+json">
                    {JSON.stringify(schemaData)}
                </script>
            </Helmet>

            <AgeGate onVerify={() => setAgeVerified(true)} />

            <AnimatePresence>
                {loading && <Loader setLoading={setLoading} />}
            </AnimatePresence>

            {!loading && ageVerified && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8 }}
                >
                    <Navbar />
                    <Hero />
                    <Gallery />
                    <ReservationForm />
                    <Marquee />
                    <Contacts />
                    <Footer />
                </motion.div>
            )}
        </div>
    );
}

export default App;

