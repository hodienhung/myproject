document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('snowCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    function setCanvasSize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    let snowflakes = [];
    const numberOfSnowflakes = 250;

    function createSnowflake() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 3 + 1,
            speed: Math.random() * 1.5 + 0.5,
            sway: Math.random() * 0.5 - 0.25,
            opacity: Math.random() * 0.6 + 0.3
        };
    }

    for (let i = 0; i < numberOfSnowflakes; i++) {
        snowflakes.push(createSnowflake());
    }

    function drawAndAnimate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < numberOfSnowflakes; i++) {
            const s = snowflakes[i];

            s.y += s.speed;
            s.x += s.sway * Math.sin(s.y * 0.01);

            ctx.beginPath();
            ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${s.opacity})`;
            ctx.fill();

            if (s.y > canvas.height) {
                snowflakes[i] = createSnowflake();
                snowflakes[i].y = -s.radius;
            }
        }

        requestAnimationFrame(drawAndAnimate);
    }

    drawAndAnimate();
});
