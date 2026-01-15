import React from 'react';

const Marquee = () => {
    return (
        <div className="marquee-strip">
            <div className="marquee-content">
                {Array(8).fill(null).map((_, i) => (
                    <React.Fragment key={i}>
                        <span>HOOKAH PLACE</span>
                        <span className="separator">-</span>
                        <span>NOBLE</span>
                        <span className="separator">-</span>
                        <span>SOCHI</span>
                        <span className="separator">-</span>
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
};

export default Marquee;
