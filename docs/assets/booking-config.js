/* Second Context 예약·결제 설정 (2026-11-16, 로컬 초안). 예약 주소는 이 파일 한곳에서만 바꾼다.
   - freeConsultUrl: 무료 30분 상담(Calendly). 상담 언어(한국어/영어) 질문은 Calendly 이벤트 설정에서 추가해야 한다
   - paidReviewUrl: 유료 60분 집중 UX 리뷰 Stripe 결제 링크(2026-11-18 사용자 제공, US$200). 결제만 받고 일정은 결제 후 이메일로 정한다.
     비어 있으면 페이지는 '리뷰 신청 문의'(문의 폼, 리뷰 미리 선택)와 '온라인 결제 연결 준비 중' 안내를 보여 준다.
     주소를 넣으면 [data-paid-review-link] 버튼이 그 주소로 보이고, 준비 중 안내([data-paid-pending])는 숨는다.
   - paidSprintUrl: UX 진단 스프린트 Stripe 결제 링크(2026-11-18 사용자 제공). 고객이 확정된 견적 금액을 직접 입력하는 링크라
     '진단 범위 문의'가 먼저이고, '견적 확정 후 결제' 버튼([data-sprint-link])은 보조로 둔다. [data-sprint-pending]/[data-sprint-ready]로 문구 전환
   - paidProjectUrl: 복잡한 제품 흐름 개선 스프린트 Stripe 결제 링크(2026-11-18 사용자 제공, 금액 직접 입력). 스프린트와 같은 방식([data-project-*])
   무료 상담 링크를 paidReviewUrl에 넣지 않는다. 가짜 결제 링크·결제 성공 상태를 만들지 않는다. */
window.SC_BOOKING = {
  freeConsultUrl: 'https://calendly.com/yeagyeong/meeting-with-rachel-cho',
  paidReviewUrl: 'https://buy.stripe.com/7sY6oIbhC5C06zd01X7N600',
  paidSprintUrl: 'https://buy.stripe.com/fZu3cwgBWfcA9Lp4id7N601',
  paidProjectUrl: 'https://buy.stripe.com/fZu8wQady3tSaPt4id7N602'
};

(function () {
  var free = window.SC_BOOKING.freeConsultUrl;
  // 서비스별 결제 링크: [링크 속성, 연결 전 문구, 연결 후 문구]
  var SETS = [
    [window.SC_BOOKING.paidReviewUrl, 'data-paid-review-link', 'data-paid-pending', 'data-paid-ready'],
    [window.SC_BOOKING.paidSprintUrl, 'data-sprint-link', 'data-sprint-pending', 'data-sprint-ready'],
    [window.SC_BOOKING.paidProjectUrl, 'data-project-link', 'data-project-pending', 'data-project-ready']
  ];
  function all(attr) { return Array.prototype.slice.call(document.querySelectorAll('[' + attr + ']')); }
  document.addEventListener('DOMContentLoaded', function () {
    SETS.forEach(function (set) {
      var url = (set[0] || '').trim();
      // 비어 있거나 무료 상담 주소가 잘못 들어가면 유료 버튼을 켜지 않는다
      if (!url || url === free) return;
      all(set[1]).forEach(function (a) { a.href = url; a.hidden = false; });
      all(set[2]).forEach(function (el) { el.hidden = true; });
      all(set[3]).forEach(function (el) { el.hidden = false; });
    });
  });
})();
