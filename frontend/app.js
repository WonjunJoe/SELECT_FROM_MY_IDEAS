/**
 * Select From My Ideas - Frontend App
 * Paper & Ink Editorial Edition
 */

const API_BASE = 'http://localhost:8000';

// ===== STATE =====
const state = {
  sessionId: null,
  currentRound: 1,
  maxRounds: 5,
  selections: {},
  originalInput: '',
  currentData: null,
};

// ===== DOM ELEMENTS =====
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const elements = {
  // Screens
  screenWelcome: $('#screenWelcome'),
  screenQuestions: $('#screenQuestions'),
  screenLoading: $('#screenLoading'),
  screenResults: $('#screenResults'),

  // Round indicator
  roundIndicator: $('#roundIndicator'),
  roundDots: $('#roundDots'),
  roundLabel: $('#roundLabel'),

  // Welcome
  ideaInput: $('#ideaInput'),
  btnStart: $('#btnStart'),

  // Questions
  contextSummary: $('#contextSummary'),
  questionsList: $('#questionsList'),
  btnBack: $('#btnBack'),
  btnNext: $('#btnNext'),

  // Results
  resultSummaryText: $('#resultSummaryText'),
  actionList: $('#actionList'),
  tipsList: $('#tipsList'),
  insightsList: $('#insightsList'),
  nextStepsText: $('#nextStepsText'),
  encouragementText: $('#encouragementText'),
  btnRestart: $('#btnRestart'),
};


// ===== SCREEN MANAGEMENT =====
function showScreen(screenId) {
  $$('.screen').forEach(screen => {
    screen.classList.remove('active');
  });

  const targetScreen = $(`#${screenId}`);
  if (targetScreen) {
    // Small delay for transition effect
    requestAnimationFrame(() => {
      targetScreen.classList.add('active');
    });
  }

  // Round indicator visibility
  if (screenId === 'screenQuestions') {
    elements.roundIndicator.classList.add('visible');
  } else {
    elements.roundIndicator.classList.remove('visible');
  }
}


function updateRoundIndicator(round) {
  const dots = elements.roundDots.querySelectorAll('.dot');
  dots.forEach((dot, index) => {
    dot.classList.remove('active', 'completed');
    if (index < round - 1) {
      dot.classList.add('completed');
    } else if (index === round - 1) {
      dot.classList.add('active');
    }
  });

  elements.roundLabel.textContent = `Round ${round} of ${state.maxRounds}`;
}


// ===== API CALLS =====
async function startSession(input) {
  try {
    const response = await fetch(`${API_BASE}/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input }),
    });

    if (!response.ok) throw new Error('Failed to start session');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return mockStartSession(input);
  }
}


async function submitSelections(sessionId, selections) {
  try {
    const response = await fetch(`${API_BASE}/session/${sessionId}/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ selections }),
    });

    if (!response.ok) throw new Error('Failed to submit selections');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return mockSubmitSelections(state.currentRound);
  }
}


// ===== MOCK DATA =====
function mockStartSession(input) {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        session_id: 'demo-' + Date.now(),
        summary: `"${input.slice(0, 50)}${input.length > 50 ? '...' : ''}" - 좋은 시작이에요! 조금만 더 구체적으로 만들어볼게요.`,
        selections: [
          {
            question: '이번 주에 딱 한 번, 10분만 시간을 낸다면 뭘 해볼까요?',
            options: [
              '관련 유튜브 영상 1개 찾아서 저장해두기',
              '노션/메모장에 아이디어 3줄로 정리하기',
              '비슷한 걸 하는 사람 SNS에서 1명 찾아보기',
              '가장 쉬운 첫 단계 1개만 적어보기'
            ],
            allow_other: true
          },
          {
            question: '현실적으로 이걸 할 수 있는 시간대는 언제인가요?',
            options: [
              '아침 출근 전 (6:00-8:00)',
              '점심시간 (12:00-13:00)',
              '퇴근 후 저녁 (19:00-22:00)',
              '주말 오전 (토/일 10:00-12:00)'
            ],
            allow_other: true
          }
        ],
        should_conclude: false
      });
    }, 1200);
  });
}


function mockSubmitSelections(round) {
  return new Promise(resolve => {
    setTimeout(() => {
      if (round >= 2) {
        resolve({
          final_output: {
            final_summary: '퇴근 후 집에서 유튜브로 관련 영상을 보면서 시작하기로 했어요. 첫 시작은 내일 저녁 8시입니다!',
            action_items: [
              {
                action: '지금 바로: 유튜브에서 관련 키워드 검색 → 첫 번째 영상 "나중에 볼 동영상"에 저장',
                priority: 'high',
                effort: 'minimal'
              },
              {
                action: '오늘 자기 전: 내일 저녁 8시 알람 설정, 알람 이름 "10분 도전"으로 변경',
                priority: 'high',
                effort: 'minimal'
              },
              {
                action: '내일 저녁 8시: 저장해둔 영상 틀고 10분 집중해서 보기',
                priority: 'high',
                effort: 'minimal'
              },
              {
                action: '이번 주 일요일: 3일 실천했는지 체크, 다음 주 계획 세우기',
                priority: 'medium',
                effort: 'minimal'
              }
            ],
            tips: [
              '완벽하게 하려고 하지 마세요 - 10분만 해도 성공입니다!',
              '같은 시간에 하면 습관이 더 빨리 자리잡아요',
              '기록하지 않아도 돼요. 일단 하는 게 핵심!'
            ],
            insights: [
              '퇴근 후 시간을 선택하신 건 아침에 여유가 없다는 뜻이에요. 저녁 루틴에 자연스럽게 끼워넣는 게 성공 확률이 높습니다.',
              '유튜브를 선택하신 건 혼자 조용히 시작하는 걸 선호하신다는 의미일 수 있어요.'
            ],
            next_steps: '지금: 유튜브 영상 저장 (1분)\n오늘 밤: 알람 설정 (30초)\n내일 저녁 8시: 첫 도전 10분',
            encouragement: '작은 시작이 큰 변화를 만들어요. 내일 저녁 8시에 만나요!'
          }
        });
      } else {
        resolve({
          summary: '좋아요! 조금 더 구체적으로 정해볼게요.',
          selections: [
            {
              question: '첫 시작은 언제 해볼까요?',
              options: [
                '오늘 저녁 (바로 시작)',
                '내일 저녁 (하루 준비)',
                '이번 주 토요일 (주말에 여유있게)',
                '다음 주 월요일 (새로운 시작)'
              ],
              allow_other: true
            },
            {
              question: '시작 전에 뭘 해두면 좋을까요?',
              options: [
                '관련 영상/글 1개 미리 저장해두기',
                '캘린더에 알람 설정하기',
                '필요한 도구/앱 설치하기',
                '준비 없이 바로 시작하기'
              ],
              allow_other: true
            }
          ],
          should_conclude: false
        });
      }
    }, 1500);
  });
}


// ===== RENDER FUNCTIONS =====
function renderQuestions(data) {
  state.currentData = data;
  elements.contextSummary.textContent = data.summary;
  elements.questionsList.innerHTML = '';
  state.selections = {};

  data.selections.forEach((selection, qIndex) => {
    const questionBlock = document.createElement('div');
    questionBlock.className = 'question-block';

    let optionsHtml = selection.options.map((option, oIndex) => `
      <button class="option-btn" data-question="${qIndex}" data-option="${oIndex}">
        <span class="option-radio"></span>
        <span class="option-text">${option}</span>
      </button>
    `).join('');

    if (selection.allow_other) {
      optionsHtml += `
        <button class="option-btn" data-question="${qIndex}" data-option="other">
          <span class="option-radio"></span>
          <span class="option-text">기타 (직접 입력)</span>
        </button>
        <div class="custom-input-wrapper" id="customInput${qIndex}">
          <input type="text" class="custom-input" placeholder="직접 입력해주세요..." data-question="${qIndex}">
        </div>
      `;
    }

    questionBlock.innerHTML = `
      <div class="question-number">Q${qIndex + 1}</div>
      <h3 class="question-title">${selection.question}</h3>
      <div class="options-list">${optionsHtml}</div>
    `;

    elements.questionsList.appendChild(questionBlock);
  });

  // Event listeners
  $$('.option-btn').forEach(btn => {
    btn.addEventListener('click', handleOptionClick);
  });

  $$('.custom-input').forEach(input => {
    input.addEventListener('input', handleCustomInput);
  });

  updateNextButton();
}


function handleOptionClick(e) {
  const btn = e.currentTarget;
  const questionIndex = btn.dataset.question;
  const optionIndex = btn.dataset.option;

  // Remove selection from siblings
  $$(`.option-btn[data-question="${questionIndex}"]`).forEach(b => {
    b.classList.remove('selected');
  });

  btn.classList.add('selected');

  // Handle custom input
  const customWrapper = $(`#customInput${questionIndex}`);
  if (customWrapper) {
    if (optionIndex === 'other') {
      customWrapper.classList.add('visible');
      customWrapper.querySelector('.custom-input').focus();
      state.selections[questionIndex] = { type: 'custom', value: '' };
    } else {
      customWrapper.classList.remove('visible');
      state.selections[questionIndex] = {
        type: 'option',
        value: btn.querySelector('.option-text').textContent
      };
    }
  } else {
    state.selections[questionIndex] = {
      type: 'option',
      value: btn.querySelector('.option-text').textContent
    };
  }

  updateNextButton();
}


function handleCustomInput(e) {
  const questionIndex = e.target.dataset.question;
  state.selections[questionIndex] = { type: 'custom', value: e.target.value };
  updateNextButton();
}


function updateNextButton() {
  const questionCount = $$('.question-block').length;
  const answeredCount = Object.keys(state.selections).filter(key => {
    const sel = state.selections[key];
    return sel.type === 'option' || (sel.type === 'custom' && sel.value.trim());
  }).length;

  elements.btnNext.disabled = answeredCount < questionCount;
}


function renderResults(finalOutput) {
  // Summary
  elements.resultSummaryText.textContent = finalOutput.final_summary;

  // Action Items
  elements.actionList.innerHTML = finalOutput.action_items.map((item, index) => `
    <li class="action-item priority-${item.priority}">
      <span class="action-number">${index + 1}</span>
      <div class="action-content">
        <p class="action-text">${item.action}</p>
        <div class="action-meta">
          <span class="action-tag">${getPriorityLabel(item.priority)}</span>
          <span class="action-tag">${getEffortLabel(item.effort)}</span>
        </div>
      </div>
    </li>
  `).join('');

  // Tips
  elements.tipsList.innerHTML = finalOutput.tips.map(tip => `
    <li>${tip}</li>
  `).join('');

  // Insights
  elements.insightsList.innerHTML = finalOutput.insights.map(insight => `
    <li>${insight}</li>
  `).join('');

  // Next Steps
  elements.nextStepsText.textContent = finalOutput.next_steps;

  // Encouragement
  elements.encouragementText.textContent = finalOutput.encouragement;
}


function getPriorityLabel(priority) {
  const labels = {
    high: '우선',
    medium: '보통',
    low: '나중에'
  };
  return labels[priority] || priority;
}


function getEffortLabel(effort) {
  const labels = {
    minimal: '쉬움',
    moderate: '보통',
    significant: '시간 필요'
  };
  return labels[effort] || effort;
}


// ===== EVENT HANDLERS =====
async function handleStart() {
  const input = elements.ideaInput.value.trim();
  if (!input) {
    elements.ideaInput.focus();
    return;
  }

  state.originalInput = input;
  showScreen('screenLoading');

  const data = await startSession(input);

  state.sessionId = data.session_id;
  state.currentRound = 1;

  if (data.final_output) {
    renderResults(data.final_output);
    showScreen('screenResults');
  } else {
    updateRoundIndicator(state.currentRound);
    renderQuestions(data);
    showScreen('screenQuestions');
  }
}


async function handleNext() {
  const selections = Object.entries(state.selections).map(([qIndex, sel]) => ({
    question: $$('.question-title')[qIndex].textContent,
    selected_option: sel.type === 'option' ? sel.value : null,
    custom_input: sel.type === 'custom' ? sel.value : null,
  }));

  showScreen('screenLoading');

  const data = await submitSelections(state.sessionId, selections);

  if (data.final_output) {
    renderResults(data.final_output);
    showScreen('screenResults');
  } else {
    state.currentRound++;
    updateRoundIndicator(state.currentRound);
    renderQuestions(data);
    showScreen('screenQuestions');
  }
}


function handleBack() {
  resetState();
  showScreen('screenWelcome');
}


function handleRestart() {
  resetState();
  elements.ideaInput.value = '';
  showScreen('screenWelcome');
  elements.ideaInput.focus();
}


function resetState() {
  state.sessionId = null;
  state.currentRound = 1;
  state.selections = {};
  state.originalInput = '';
  state.currentData = null;
}


function handleExampleClick(e) {
  const example = e.target.dataset.example;
  if (example) {
    elements.ideaInput.value = example;
    elements.ideaInput.focus();

    // Visual feedback
    e.target.style.transform = 'scale(0.95)';
    setTimeout(() => {
      e.target.style.transform = '';
    }, 150);
  }
}


// ===== INITIALIZATION =====
function init() {
  // Button events
  elements.btnStart.addEventListener('click', handleStart);
  elements.btnNext.addEventListener('click', handleNext);
  elements.btnBack.addEventListener('click', handleBack);
  elements.btnRestart.addEventListener('click', handleRestart);

  // Example tags
  $$('.tag').forEach(tag => {
    tag.addEventListener('click', handleExampleClick);
  });

  // Enter key to start
  elements.ideaInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleStart();
    }
  });

  // Focus input on load
  setTimeout(() => {
    elements.ideaInput.focus();
  }, 800);
}


// Expose handleRestart for logo click
window.handleRestart = handleRestart;

// Start
init();
