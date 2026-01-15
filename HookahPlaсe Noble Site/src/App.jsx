import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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

    return (
        <div className="app-container">
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

