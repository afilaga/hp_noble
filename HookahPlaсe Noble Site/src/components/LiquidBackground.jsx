import React, { useState, useEffect } from 'react';
import { Warp } from '@paper-design/shaders-react';

const LiquidBackground = () => {
    const [dimensions, setDimensions] = useState({
        width: window.innerWidth,
        height: window.innerHeight
    });

    useEffect(() => {
        const handleResize = () => {
            setDimensions({
                width: window.innerWidth,
                height: window.innerHeight
            });
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return (
        <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            zIndex: 0,
            overflow: 'hidden',
            pointerEvents: 'none',
            background: '#000'
        }}>
            <div style={{
                width: '100%',
                height: '100%',
                transform: 'scale(1.05)', // Slightly larger scale to ensure coverage
                filter: 'blur(10px)', // Blur helps hide the lower resolution
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <Warp
                    width={Math.ceil(dimensions.width / 3)}
                    height={Math.ceil(dimensions.height / 3)}
                    colors={["#e1ae75", "#6b542e", "#000000", "#82694a"]}
                    proportion={0.64}
                    softness={1.5} // Increased softness to help blending
                    distortion={0.15} // Reduced slightly for stability
                    swirl={0.5}
                    swirlIterations={4} // Aggressively reduced
                    shape="checks"
                    shapeScale={0.45}
                    speed={0.6} // Slower is less demanding
                    scale={2.2}
                    rotation={36}
                    style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover'
                    }}
                />
            </div>
        </div>
    );
};

export default LiquidBackground;
