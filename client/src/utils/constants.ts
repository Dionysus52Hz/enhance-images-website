import {
   Pill,
   Tablets,
   Store,
   Factory,
   UsersRound,
   UserRoundPen,
   History,
   Contact,
   FileInput,
   FileOutput,
   ChartNoAxesCombined,
   HardDriveDownload,
   HardDriveUpload,
   UserRoundCheck,
   KeyRound,
   Settings,
   LogOut,
   Sparkle,
   WandSparkles,
} from 'lucide-vue-next';

const MENU_ITEMS = [
   {
      title: 'Tools',
      items: [
         {
            icon: Sparkle,
            text: 'Enhancer',
            view: 'enhancer-view',
         },
         {
            icon: WandSparkles,
            text: 'Filters',
            view: 'filters-view',
         },
      ],
   },
   {
      title: 'Accounts',
      items: [
         {
            icon: UsersRound,
            text: 'Profile',
            view: 'profile-view',
         },
         {
            icon: History,
            text: 'History',
            view: 'history-view',
         },
      ],
   },
];

export { MENU_ITEMS };
