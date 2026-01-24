<template>
  <main>
    <div class="page">
      <div class="links">
        <a class="link-text" href="https://github.com/kabsmeiou/ossanimap" target="_blank" rel="noopener noreferrer">Github</a>
        <!-- <a class="link-text" href="https://api.kabsmeiou.space/docs" target="_blank" rel="noopener noreferrer">API Docs</a> -->
        <a class="link-text" href="https://catboy.best" target="_blank" rel="noopener noreferrer">Chimu</a>
        <a class="link-text" href="https://animethemes.moe" target="_blank" rel="noopener noreferrer">Animethemes</a>
      </div>
      <header class="top">
        <div class="brand"> 
          <div class="logo">
            <!-- use favicon.ico -->
            <img src="/favicon.ico" alt="ossanimap Logo" width="34" height="34" />
          </div>
          <div class="header-text">
            <h1>ossanimap</h1>
            <p class="tagline">your favorite anime beatmap packs in one place</p>
          </div>
        </div>
      </header>
      <router-view></router-view>
    </div>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  padding : 0px 0px 32px 0px ;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.links {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 12px;
  z-index: 200;
}

.link-text{
  font-size: 14px;
  color: #4a5568;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s ease;
  border-radius: 1rem;
  padding: 4px 8px;
}
.link-text:hover {
  background-color: #c5cbe2;
}
@media screen and (max-width: 1100px) {
  .links {
    padding: 1rem;
    position: static;
    justify-content: center;
  }
}
.top {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
}
.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tagline {
  font-size: 14px;
  color: #718096;
  margin: 0;
  font-weight: 500;
}

.brand .logo {
  width: 3rem;
  height: 3rem;
  border-radius: 12px;
  border-color: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* apply gradient to text */
.brand h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>