using button.Models;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace button.Controllers
{
    public class HomeController : Controller
    {
        private readonly ButtonclickContext _context;

        public HomeController(ButtonclickContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            return View();
        }

        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
