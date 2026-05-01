const Header = () => {
  return (
    <header className="fixed top-0 left-0 right-0 bg-primary/90 backdrop-blur-md text-white shadow-lg z-10 border-b border-white/20">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">💜</span>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight">Zyra</h1>
        </div>
        <div className="hidden md:block text-sm opacity-80">
          Your AI Friend
        </div>
        <div className="md:hidden text-sm opacity-80">
          ✨ AI
        </div>
      </div>
    </header>
  );
};

export default Header;