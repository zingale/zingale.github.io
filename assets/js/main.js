/*
	Halcyonic by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {

	var $window = $(window),
		$body = $('body');

	// Breakpoints.
		breakpoints({
			xlarge:  [ '1281px',  '1680px' ],
			large:   [ '981px',   '1280px' ],
			medium:  [ '737px',   '980px'  ],
			small:   [ null,      '736px'  ]
		});

	// Nav.

		// Title Bar.
			$(
				'<div id="titleBar">' +
					'<a href="#navPanel" class="toggle" role="button" aria-label="Navigation" aria-controls="navPanel" aria-expanded="false"></a>' +
					'<span class="title">' + $('#logo').html() + '</span>' +
				'</div>'
			)
				.appendTo($body);

		// Panel.
			$(
				'<div id="navPanel">' +
					'<nav aria-label="Primary">' +
						$('#nav').navList() +
					'</nav>' +
				'</div>'
			)
				.appendTo($body)
				.panel({
					delay: 500,
					hideOnClick: true,
					hideOnEscape: true,
					hideOnSwipe: true,
					resetScroll: true,
					resetForms: true,
					side: 'left',
					target: $body,
					visibleClass: 'navPanel-visible'
				});

		// Keep the disclosure state and keyboard focus in sync, including
		// when the panel is dismissed by a swipe or a click outside it.
		var toggle = document.querySelector('#titleBar .toggle'),
			panel = document.getElementById('navPanel');

		$(toggle).on('keydown', function(event) {
			if (event.key === ' ') {
				event.preventDefault();
				$(this).trigger('click');
			}
		});

		new MutationObserver(function() {
			var open = $body.hasClass('navPanel-visible');
			if (toggle.getAttribute('aria-expanded') === String(open))
				return;
			toggle.setAttribute('aria-expanded', String(open));
			if (open) {
				var firstLink = panel.querySelector('a');
				if (firstLink) firstLink.focus();
			} else if (panel.contains(document.activeElement)) {
				toggle.focus();
			}
		}).observe(document.body, { attributes: true, attributeFilter: ['class'] });

		$(panel).on('focusout', function(event) {
			if (!panel.contains(event.relatedTarget) && event.relatedTarget !== toggle)
				$body.removeClass('navPanel-visible');
		});

		$window.on('resize', function() {
			if (window.matchMedia('(min-width: 981px)').matches) {
				if (panel.contains(document.activeElement) || document.activeElement === toggle) {
					var desktopLink = document.querySelector('#nav a');
					if (desktopLink) desktopLink.focus();
				}
				$body.removeClass('navPanel-visible');
			}
		});

})(jQuery);
