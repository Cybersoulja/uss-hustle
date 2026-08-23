// =============================================================================
// Cloudflare Worker: Space Age Hustle Telegram Webhook Gateway
// =============================================================================

export interface Env {
  DB: D1Database;
  STORY_KV: KVNamespace;
  TELEGRAM_BOT_TOKEN: string;
  AI: any;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
      return new Response('USS Hustle Space Gateway Online 🚀', { status: 200 });
    }

    try {
      const update = await request.json<any>();
      if (update.message) {
        await handleMessage(update.message, env);
      }
      return new Response('OK', { status: 200 });
    } catch (err: any) {
      return new Response(`Error: ${err.message}`, { status: 500 });
    }
  }
};

async function handleMessage(msg: any, env: Env) {
  const chatId = msg.chat.id;
  const text = msg.text?.trim() || '';

  if (text.startsWith('/start')) {
    await sendTelegram(env, chatId, 
      `🛸 *WELCOME TO SPACE AGE HUSTLE!* (Anti-Gravity v1.0)\n\n` +
      `Trill Astro Buzz reporting for duty, Commander.\n` +
      `Gravity is offline. Velocity is uncapped.\n\n` +
      `Commands:\n` +
      `• /crew — Inspect your floating agent roster\n` +
      `• /missions — View active orbital quests\n` +
      `• /checkin — Report work progress & claim XP\n` +
      `• /motivate — Receive floating motivation`
    );
  } else if (text.startsWith('/crew')) {
    await sendTelegram(env, chatId,
      `🪐 *FLOATING CREW ROSTER*\n\n` +
      `🚀 *Trill Astro Buzz* — [LEGEND] ⭐⭐⭐⭐⭐\n` +
      `   "The grind never stops." (Energy: 100% | Loyalty: MAX)\n\n` +
      `🌠 *Nova Starwind* — [EXPERT] ⭐⭐⭐⭐\n` +
      `   "Clean code from orbit." (Energy: 90% | Loyalty: 85%)\n\n` +
      `🔭 *Orion Codex* — [VETERAN] ⭐⭐⭐\n` +
      `   "Plasma shield standing by." (Energy: 95% | Loyalty: 80%)\n\n` +
      `💫 _All agents floating in zero-gravity harmony._`
    );
  } else if (text.startsWith('/motivate')) {
    const quotes = [
      "Every commit is a step on the moon of progress.",
      "The galaxy doesn't wait. Neither should your PRs.",
      "You're not just shipping code — you're shipping DESTINY.",
      "Coffee: the dark matter that powers the universe."
    ];
    const pick = quotes[Math.floor(Math.random() * quotes.length)];
    await sendTelegram(env, chatId, `🛰️ *Trill Astro Buzz Floating Dispatch:*\n\n💬 _"${pick}"_`);
  }
}

async function sendTelegram(env: Env, chatId: number, text: string) {
  const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: 'Markdown'
    })
  });
}
