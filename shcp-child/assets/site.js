// Spec tabs, mobile menu, contact form success/fail panels.
document.addEventListener('click', function (e) {
	var tab = e.target.closest('.shcp-spec-tabs button');
	if (tab && !tab.disabled) {
		var tabs = [].slice.call(tab.parentNode.children);
		var panels = tab.closest('.shcp-spec').querySelectorAll('.shcp-spec-panel');
		tabs.forEach(function (b, i) {
			b.setAttribute('aria-selected', b === tab);
			panels[i].hidden = b !== tab;
		});
	}

	var burger = e.target.closest('.shcp-burger');
	if (burger) {
		var open = burger.closest('.shcp-header').classList.toggle('is-open');
		burger.setAttribute('aria-expanded', open);
	}

	var back = e.target.closest('.shcp-form-card [data-back]');
	if (back) {
		showState(back.closest('.shcp-form-card'), null);
	}
});

function showState(card, state) {
	card.querySelector('.wpcf7').hidden = !!state;
	card.querySelectorAll('.shcp-form-state').forEach(function (el) {
		el.hidden = el.dataset.state !== state;
	});
	card.scrollIntoView({ block: 'center' });
}

document.addEventListener('wpcf7mailsent', function (e) {
	var card = e.target.closest('.shcp-form-card');
	if (!card) return;
	var msg = card.querySelector('[data-state="ok"] .shcp-form-state__msg');
	var name = e.target.querySelector('[name="full-name"]').value;
	var email = e.target.querySelector('[name="your-email"]').value;
	msg.textContent = msg.dataset.template.replace('[full-name]', name.split(' ')[0]).replace('[your-email]', email);
	showState(card, 'ok');
});

document.addEventListener('wpcf7mailfailed', function (e) {
	var card = e.target.closest('.shcp-form-card');
	if (card) showState(card, 'fail');
});

// Lock page scroll while the full-screen mobile menu is open; close it after choosing a link.
document.addEventListener('click', function (e) {
	var header = document.querySelector('.shcp-header');
	if (!header) return;
	if (e.target.closest('.shcp-header.is-open .shcp-nav a')) {
		header.classList.remove('is-open');
	}
	document.body.classList.toggle('shcp-menu-open', header.classList.contains('is-open'));
});

// Homepage hero carousel: fade every 6s, pause on hover/focus, dots and swipe.
document.querySelectorAll('.shcp-slider').forEach(function (slider) {
	var slides = slider.querySelectorAll('.shcp-slide');
	var dots = slider.querySelectorAll('.shcp-slider__dots button');
	var current = 0, timer, startX;
	if (slides.length < 2) return;

	function go(n) {
		// the hero is as tall as the active slide: ease between heights instead of jumping
		var from = slider.offsetHeight;
		slider.style.height = from + 'px';
		slides[current].classList.remove('is-active');
		slides[current].setAttribute('aria-hidden', 'true');
		dots[current].removeAttribute('aria-current');
		current = (n + slides.length) % slides.length;
		slides[current].classList.add('is-active');
		slides[current].removeAttribute('aria-hidden');
		dots[current].setAttribute('aria-current', 'true');
		var to = slides[current].offsetHeight;
		requestAnimationFrame(function () { slider.style.height = to + 'px'; });
		setTimeout(function () { slider.style.height = ''; }, 600);
	}
	function stop() { clearInterval(timer); }
	function play() {
		stop();
		if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
			timer = setInterval(function () { go(current + 1); }, 6000);
		}
	}

	dots.forEach(function (dot, n) { dot.addEventListener('click', function () { go(n); play(); }); });
	slider.addEventListener('mouseenter', stop);
	slider.addEventListener('mouseleave', play);
	slider.addEventListener('focusin', stop);
	slider.addEventListener('focusout', play);
	slider.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
	slider.addEventListener('touchend', function (e) {
		var dx = e.changedTouches[0].clientX - startX;
		if (Math.abs(dx) > 40) { go(current + (dx < 0 ? 1 : -1)); play(); }
	});
	play();
});

// Section reveal: add .is-in when a section scrolls into view (styles in style.css).
(function () {
	var root = document.documentElement;
	if (!root.classList.contains('shcp-js')) return;
	var sections = document.querySelectorAll(':is([data-elementor-type="wp-page"], [data-elementor-type="single-post"]) > .e-con:not(:first-child)');
	if (!('IntersectionObserver' in window)) {
		sections.forEach(function (s) { s.classList.add('is-in'); });
	} else {
		var io = new IntersectionObserver(function (entries) {
			entries.forEach(function (e) {
				if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
			});
		}, { rootMargin: '0px 0px -8% 0px' });
		sections.forEach(function (s) { io.observe(s); });
	}
	root.classList.add('shcp-ready');
})();
